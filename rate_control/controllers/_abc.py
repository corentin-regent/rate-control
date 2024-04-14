__all__ = [
    'RateController',
]

import sys
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Optional

from rate_control._errors import RateLimit
from rate_control._helpers import mk_repr
from rate_control._helpers._validation import validate_max_concurrency
from rate_control.buckets import Bucket

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Iterator
else:
    from typing import AsyncIterator, Iterator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class RateController(ABC):
    """Abstract base class for rate controllers."""

    def __init__(self, bucket: Bucket, max_concurrency: Optional[int] = None, **kwargs: Any) -> None:
        """
        Args:
            bucket: The bucket that will be managed by the rate controller.
            max_concurrency: The maximum amount of concurrent requests allowed.
                Defaults to `None` (no limit).
        """
        super().__init__(**kwargs)
        validate_max_concurrency(max_concurrency)
        self._bucket = bucket
        self._max_concurrency = max_concurrency
        self._concurrent_requests = 0

    async def __aenter__(self) -> Self:
        """Enter the controller's context."""
        return self

    async def __aexit__(self, *_: Any) -> Optional[bool]:
        """Exit the scheduler's context."""

    @override
    def __repr__(self) -> str:
        return mk_repr(self, bucket=self._bucket, max_concurrency=self._max_concurrency)

    def can_acquire(self, tokens: float = 1) -> bool:
        """
        Args:
            tokens: The amount of tokens to acquire for the request.
                Defaults to `1`.

        Returns:
            Whether a request for the given amount of tokens can be processed instantly.
        """
        return not self._is_concurrency_limited and self._bucket.can_acquire(tokens)

    @asynccontextmanager
    @abstractmethod
    async def request(self, tokens: float = 1) -> AsyncIterator[None]:
        """Asynchronous context manager that requests the given amount of tokens before the execution.

        Args:
            tokens: The number of tokens required for the request.
                Defaults to `1`.
        """
        yield  # pragma: no cover

    @property
    def _is_concurrency_limited(self) -> bool:
        return self._max_concurrency is not None and self._concurrent_requests >= self._max_concurrency

    def _assert_can_acquire(self, tokens: float) -> None:
        """Make sure that the request for the given amount of tokens can be processed.

        Args:
            tokens: The amount of tokens to acquire.

        Raises:
            RateLimit: Cannot process the request for the given amount of tokens.
        """
        if not self.can_acquire(tokens):
            raise RateLimit(f'Cannot process the request for {tokens} tokens.')

    @contextmanager
    def _hold_concurrency(self) -> Iterator[None]:
        """Context manager that handles concurrency management during the execution of a request."""
        self._concurrent_requests += 1
        try:
            yield
        finally:
            self._concurrent_requests -= 1
            self._on_concurrency_release()

    def _on_concurrency_release(self) -> None:
        """Perform additional operations when the amount of concurrent requests lowers."""
