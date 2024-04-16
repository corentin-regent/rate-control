__all__ = [
    'RateLimiter',
]

import sys
from contextlib import asynccontextmanager

from rate_control._controllers._abc import RateController

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class RateLimiter(RateController):
    """Rate controller that raises an error if a request cannot be fulfilled instantly."""

    @asynccontextmanager
    @override
    async def request(self, tokens: float = 1) -> AsyncIterator[None]:
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