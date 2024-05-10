__all__ = [
    'Scheduler',
]

import sys
from contextlib import asynccontextmanager, suppress
from typing import Any, NoReturn, Optional

from anyio import create_task_group, get_cancelled_exc_class
from anyio.lowlevel import checkpoint

from rate_control._buckets import Bucket
from rate_control._controllers._abc import RateController
from rate_control._controllers._bucket_based import BucketBasedRateController
from rate_control._enums import Priority, State
from rate_control._errors import RateLimit, ReachedMaxPending
from rate_control._helpers import ContextAware, Request, mk_repr
from rate_control._helpers._validation import validate_max_pending
from rate_control.queues import PriorityQueue, Queue

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Callable
else:
    from typing import AsyncIterator, Callable

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class Scheduler(BucketBasedRateController, ContextAware, RateController):
    """Rate controller that schedules requests for later processing."""

    def __init__(
        self,
        *buckets: Bucket,
        should_enter_context: bool = True,
        max_concurrency: Optional[int] = None,
        max_pending: Optional[int] = None,
        queue_factory: Callable[[], Queue[Request]] = PriorityQueue,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            buckets: The buckets that will be managed by the rate controller, optional.
            should_enter_context: Whether entering the context of the rate controller
                should also enter the context of the underlying buckets, if any.
                Defaults to True.
            max_concurrency: The maximum amount of concurrent requests allowed.
                Defaults to `None` (no limit).
            max_pending: The maximum amount of requests waiting to be processed.
                Defaults to `None` (no limit).
            queue_factory: The factory for initializing the request queues.
                Defaults to :class:`.PriorityQueue`: requests are processed by ascending weight.
        """
        super().__init__(*buckets, should_enter_context=should_enter_context, max_concurrency=max_concurrency, **kwargs)
        validate_max_pending(max_pending)
        self._max_pending = max_pending
        self._pending_requests = 0
        self._queues = [queue_factory() for _ in Priority]

    @override
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self._task_group = await create_task_group().__aenter__()
        if self._bucket is not None:
            self._task_group.start_soon(self._listen_to_refills)
        return self

    async def _listen_to_refills(self) -> NoReturn:
        """Process queued requests every time new tokens are available."""
        assert self._bucket is not None
        while True:
            await self._bucket.wait_for_refill()
            await self._process_queued_requests()
            await checkpoint()

    @override
    async def __aexit__(self, *exc_info: Any) -> Optional[bool]:
        self._task_group.cancel_scope.cancel()
        await self._task_group.__aexit__(*exc_info)
        return await super().__aexit__(*exc_info)

    @override
    def __repr__(self) -> str:
        return (
            mk_repr(
                self,
                self._bucket,
                should_enter_context=self._should_enter_context,
                max_concurrency=self._max_concurrency,
                max_pending=self._max_pending,
            )
            if self._bucket is not None
            else mk_repr(self, max_concurrency=self._max_concurrency, max_pending=self._max_pending)
        )

    @asynccontextmanager
    @override
    async def request(
        self,
        tokens: float = 1,
        priority: Priority = Priority.NORMAL,
        fill_or_kill: bool = False,
        **_: Any,
    ) -> AsyncIterator[None]:
        """Asynchronous context manager that schedules the execution of the contained statements.

        Waits until all the conditions of token availability and allowed concurrency are met,
        before actually consuming tokens and holding a spot for the concurrency.

        Args:
            tokens: The number of tokens required for the request.
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
        if self._state is not State.ENTERED:
            raise RuntimeError(
                f"Make sure to enter the scheduler's context using 'async with {type(self).__name__}(...)'"
            )
        if not self.can_acquire(tokens):
            if fill_or_kill:
                raise RateLimit(f'Cannot process the request for {tokens} tokens.')
            else:
                await self._schedule_request(tokens, priority)
        if self._bucket is not None:
            self._bucket.acquire(tokens)
        with self._hold_concurrency():
            yield

    @override
    def _on_concurrency_release(self) -> None:
        if self._max_concurrency is not None and self._concurrent_requests == self._max_concurrency - 1:
            self._task_group.start_soon(self._process_queued_requests)

    async def _process_queued_requests(self) -> None:
        while True:
            try:
                queue = next(queue for queue in filter(None, self._queues) if self.can_acquire(queue.head().cost))
            except StopIteration:
                break
            await self._process_next_request(queue)

    async def _process_next_request(self, queue: Queue[Request]) -> None:
        """Fire the next request from the queue and wait until the underlying tokens are acquired.

        Tokens are not acquired directly in this method,
        in order to support request cancellation.
        """
        request = queue.pop()
        self._pending_requests -= 1
        request.fire()
        await request.wait_for_ack()

    async def _schedule_request(self, tokens: float, priority: Priority) -> None:
        """Schedule an internal request to acquire the given amount of tokens, with the given priority.

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
        if self._is_pending_limited:
            raise ReachedMaxPending
        queue = self._queues[priority]
        queue.add(request)
        self._pending_requests += 1

    @property
    def _is_pending_limited(self) -> bool:
        return self._max_pending is not None and self._pending_requests >= self._max_pending

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
