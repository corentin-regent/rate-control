__all__ = [
    'Scheduler',
]

import sys
from contextlib import asynccontextmanager, contextmanager, suppress
from typing import Any, NoReturn, Optional

from anyio import create_task_group, get_cancelled_exc_class
from anyio.lowlevel import checkpoint

from rate_control._controllers._base import RateController
from rate_control._enums import Priority
from rate_control._errors import RateLimit, ReachedMaxPending
from rate_control._helpers import Request, mk_repr
from rate_control._helpers._validation import validate_max_pending
from rate_control.buckets import Bucket
from rate_control.queues import PriorityQueue, Queue

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Callable, Iterator
else:
    from typing import AsyncIterator, Callable, Iterator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class Scheduler(RateController):
    """Rate controller that schedule requests for later processing."""

    def __init__(
        self,
        bucket: Bucket,
        max_concurrency: Optional[int] = None,
        max_pending: Optional[int] = None,
        queue_factory: Callable[[], Queue[Request]] = PriorityQueue,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            bucket: The bucket that will be managed by the rate controller.
            max_concurrency: The maximum amount of concurrent requests allowed.
                Defaults to `None` (no limit).
            max_pending: The maximum amount of requests waiting to be processed.
                Defaults to `None` (no limit).
            queue_factory: The factory for initializing the request queues.
                Defaults to :class:`.PriorityQueue`: requests are processed by ascending weight.
        """
        super().__init__(bucket, max_concurrency, **kwargs)
        validate_max_pending(max_pending)
        self._max_pending = max_pending
        self._pending_requests = 0
        self._queues = [queue_factory() for _ in Priority]
        self._is_processing_requests = False

    async def __aenter__(self) -> Self:
        """Enter the scheduler's context.

        Starts listening to the underlying bucket for replenishments.
        """
        self._task_group = await create_task_group().__aenter__()
        self._task_group.start_soon(self._listen_to_refills)
        return self

    async def _listen_to_refills(self) -> NoReturn:
        """Process queued requests every time new tokens are available."""
        while True:
            await self._bucket.wait_for_refill()
            await self._process_queued_requests()
            await checkpoint()

    async def __aexit__(self, *exc_info: Any) -> None:
        """Exit the scheduler's context."""
        self._task_group.cancel_scope.cancel()
        await self._task_group.__aexit__(*exc_info)

    @override
    def __repr__(self) -> str:
        return mk_repr(self, bucket=self._bucket, max_concurrency=self._max_concurrency, max_pending=self._max_pending)

    @asynccontextmanager
    async def schedule(
        self,
        cost: float = 1,
        priority: Priority = Priority.NORMAL,
        fill_or_kill: bool = False,
    ) -> AsyncIterator[None]:
        """Asynchronous context manager that schedules the execution of the contained statements.

        Waits until all the conditions of token disponibility and allowed concurrency are met,
        before actually consuming tokens and holding a spot for the concurrency.

        Args:
            cost: The number of tokens required for the request.
                Defaults to `1`.
            priority: The priority of the request.
                Requests with higher priority will be processed before the others.
                Defaults to :py:enum:mem:`Priority.NORMAL`.
            fill_or_kill: Whether :exc:`RateLimit` should be raised
                if the request cannot be process instantly.
                Defaults to `False`.

        Raises:
            RateLimit: The request cannot be processed instantly
                but the ``fill_or_kill`` flag was set to `True`.
            ReachedMaxPending: The limit of pending requests was reached.
        """
        if not hasattr(self, '_task_group'):
            raise RuntimeError(f"Make sure to enter the scheduler's context using 'async with {self}'")
        if not self.can_acquire(cost):
            if fill_or_kill:
                raise RateLimit(f'Cannot process the request for {cost} tokens.')
            else:
                await self._request(cost, priority)
        self._bucket.acquire(cost)
        with self._hold_concurrency():
            yield

    @override
    def _on_concurrency_release(self) -> None:
        if self._max_concurrency is not None and self._concurrent_requests == self._max_concurrency - 1:
            self._task_group.start_soon(self._process_queued_requests)

    async def _process_queued_requests(self) -> None:
        """Pop and start queued requests while it is possible."""
        if self._is_processing_requests:
            return
        with self._hold_request_processing():
            await self._process_queues()

    async def _process_queues(self) -> None:
        while True:
            try:
                queue = next(filter(lambda queue: self.can_acquire(queue.head().cost), filter(None, self._queues)))
            except StopIteration:
                break
            else:
                await self._process_next_request(queue)

    @contextmanager
    def _hold_request_processing(self) -> Iterator[None]:
        self._is_processing_requests = True
        try:
            yield
        finally:
            self._is_processing_requests = False

    async def _process_next_request(self, queue: Queue[Request]) -> None:
        """Fire the next request from the queue and wait until the underlying tokens are acquired.

        Tokens are not acquired directly in this method,
        in order to support request cancellation.
        """
        request = self._pop(queue)
        request.fire()
        await request.wait_for_ack()

    async def _request(self, tokens: float, priority: Priority) -> None:
        """Perform a request to acquire the given amount of tokens, with the given priority.

        Args:
            tokens: The amount of tokens to acquire.
            priority: The request priority.

        Raises:
            ReachedMaxPending: The limit of pending requests was reached.
        """
        request = Request(tokens)
        self._enqueue(request, priority)
        try:
            await request.wait_for_validation()
        except get_cancelled_exc_class():
            self._discard(request, priority)
            raise
        finally:
            request.ack()

    def _enqueue(self, request: Request, priority: Priority) -> None:
        """Add the given request to the queue.

        Args:
            request: The request to schedule.
            priority: The priority of the request.

        Raises:
            ReachedMaxPending: The limit of pending requests was reached.
        """
        self._check_pending_limit()
        queue = self._queues[priority]
        queue.add(request)
        self._pending_requests += 1

    def _discard(self, request: Request, priority: Priority) -> None:
        """Remove the given request from the queue, if it exists.

        Args:
            request: The request to unschedule.
            priority: The priority with which the request was originally scheduled.
        """
        queue = self._queues[priority]
        with suppress(ValueError):
            queue.remove(request)
            self._pending_requests -= 1

    def _pop(self, queue: Queue[Request]) -> Request:
        request = queue.pop()
        self._pending_requests -= 1
        return request

    def _check_pending_limit(self) -> None:
        """Make sure that a new pending request can be scheduled.

        Raises:
            ReachedMaxPending: The limit of pending requests was reached.
        """
        if self._max_pending is not None and self._max_pending <= self._pending_requests:
            raise ReachedMaxPending
