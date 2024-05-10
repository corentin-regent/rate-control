__all__ = [
    'BucketGroup',
]

import sys
from contextlib import AsyncExitStack, suppress
from typing import Any, Iterator, Optional

from anyio import WouldBlock, create_memory_object_stream, create_task_group

from rate_control._buckets import Bucket
from rate_control._helpers import ContextAware, mk_repr

if sys.version_info >= (3, 9):
    from collections.abc import Iterable
else:
    from typing import Iterable

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class BucketGroup(ContextAware, Bucket, Iterable[Bucket]):
    """Composite bucket that aggregates other buckets."""

    def __init__(self, *buckets: Bucket, should_enter_context: bool = True, **kwargs: Any) -> None:
        """
        Args:
            buckets: The buckets to aggregate within this bucket group.
            should_enter_context: Whether entering the context of the bucket group
                should also enter the context of the underlying buckets.
                Defaults to `True`.
        """
        super().__init__(**kwargs)
        self._buckets = buckets
        self._should_enter_context = should_enter_context
        self._send_stream, self._recv_stream = create_memory_object_stream[Bucket]()

    @override
    def __repr__(self) -> str:
        return mk_repr(self, *self._buckets, should_enter_context=self._should_enter_context)

    @override
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self._stack = await AsyncExitStack().__aenter__()
        self._task_group = await self._stack.enter_async_context(create_task_group())
        await self._init_buckets()
        return self

    @override
    async def __aexit__(self, *exc_info: Any) -> Optional[bool]:
        self._task_group.cancel_scope.cancel()
        await self._stack.__aexit__(*exc_info)
        return await super().__aexit__(*exc_info)

    @override
    def __iter__(self) -> Iterator[Bucket]:
        return iter(self._buckets)

    async def _init_buckets(self) -> None:
        for bucket in self._buckets:
            if self._should_enter_context:
                await self._stack.enter_async_context(bucket)
            self._listen_for_refill(bucket)

    def _listen_for_refill(self, bucket: Bucket) -> None:
        self._task_group.start_soon(self._listen_for, bucket)

    async def _listen_for(self, bucket: Bucket) -> None:
        await bucket.wait_for_refill()
        await self._send_stream.send(bucket)

    @override
    async def wait_for_refill(self) -> None:
        """Wait until any of the underlying buckets refills."""
        with suppress(WouldBlock):
            while True:
                refilled_bucket = self._recv_stream.receive_nowait()
                self._listen_for_refill(refilled_bucket)
        await self._recv_stream.receive()

    @override
    def can_acquire(self, tokens: float) -> bool:
        """Whether the given amount of tokens can be acquired.

        Args:
            tokens: The amount of tokens that we want to acquire.

        Returns:
            Whether all the underlying buckets can acquire the given amount of tokens.
        """
        return all(bucket.can_acquire(tokens) for bucket in self._buckets)

    @override
    def acquire(self, tokens: float) -> None:
        """For each underlying bucket, acquire the given amount of tokens.

        Args:
            tokens: The amount of tokens to acquire.

        Raises:
            RateLimit: Any of the underlying buckets cannot acquire the given amount of tokens.
        """
        self._assert_can_acquire(tokens)
        for bucket in self._buckets:
            bucket.acquire(tokens)
