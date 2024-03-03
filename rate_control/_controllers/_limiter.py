__all__ = [
    'RateLimiter',
]

import sys
from contextlib import contextmanager

from rate_control._controllers._base import RateController

if sys.version_info >= (3, 9):
    from collections.abc import Iterator
else:
    from typing import Iterator


class RateLimiter(RateController):
    """Rate controller that raises an error if a request cannot be fulfilled instantly."""

    @contextmanager
    def hold(self, tokens: float = 1) -> Iterator[None]:
        """Context manager that acquires the given amount of tokens while holding concurrency.

        Args:
            tokens: The number of tokens to acquire.
                Defaults to `1`.
        Raises:
            RateLimit: The request cannot be fulfilled instantly.
        """
        self._assert_can_acquire(tokens)
        self._bucket.acquire(tokens)
        with self._hold_concurrency():
            yield
