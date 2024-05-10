__all__ = [
    'BaseRateBucket',
]

import sys
from abc import ABC, abstractmethod
from typing import Any, Optional

from anyio import Event, create_task_group, sleep

from rate_control._buckets._base._abc import Bucket
from rate_control._buckets._base._token_based import TokenBasedBucket
from rate_control._helpers import ContextAware
from rate_control._helpers._validation import validate_delay

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class BaseRateBucket(TokenBasedBucket, ContextAware, Bucket, ABC):
    """Base class for token buckets that refill at a certain rate."""

    def __init__(self, capacity: float, delay: float, **kwargs: Any) -> None:
        """
        Args:
            capacity: The number of tokens that can be acquired within `delay`.
            delay: The refill delay in seconds.
        """
        super().__init__(capacity, **kwargs)
        validate_delay(delay)
        self._delay = delay
        self._refill_event = Event()

    @override
    async def __aenter__(self) -> Self:
        await super().__aenter__()
        self._task_group = await create_task_group().__aenter__()
        return self

    @override
    async def __aexit__(self, *exc_info: Any) -> Optional[bool]:
        self._task_group.cancel_scope.cancel()
        await self._task_group.__aexit__(*exc_info)
        return await super().__aexit__(*exc_info)

    @override
    async def wait_for_refill(self) -> None:
        await self._refill_event.wait()

    @override
    def acquire(self, tokens: float) -> None:
        super().acquire(tokens)
        self._ensure_refill(tokens)

    def _ensure_refill(self, tokens: float = 1) -> None:
        if self._should_schedule_refill():
            try:
                self._task_group.start_soon(self._wait_and_refill, tokens)
            except AttributeError as e:
                raise RuntimeError(f"Make sure to enter the bucket's context using 'async with {self}'") from e

    @abstractmethod
    def _should_schedule_refill(self) -> bool:
        """
        Returns:
            Whether a replenishment of the bucket should be scheduled.
        """

    async def _wait_and_refill(self, tokens: float) -> None:
        await sleep(self._delay)
        self._refill(tokens)
        self._refill_event.set()
        self._refill_event = Event()

    @abstractmethod
    def _refill(self, tokens: float) -> None:
        """Add some tokens back to the bucket."""
