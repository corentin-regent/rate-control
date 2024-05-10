__all__ = [
    'RateController',
]

import sys
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Optional

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class RateController(ABC):
    """Abstract base class for rate controllers."""

    async def __aenter__(self) -> Self:
        """Enter the controller's context."""
        return self

    async def __aexit__(self, *_: Any) -> Optional[bool]:
        """Exit the controller's context."""
        return False

    @abstractmethod
    def can_acquire(self, tokens: float = 1) -> bool:
        """
        Args:
            tokens: The amount of tokens to acquire for the request.
                Defaults to `1`.

        Returns:
            Whether a request for the given amount of tokens can be processed instantly.
        """

    @asynccontextmanager
    @abstractmethod
    async def request(self, tokens: float = 1, **kwargs: Any) -> AsyncIterator[None]:
        """Asynchronous context manager that requests the given amount of tokens before execution.

        Args:
            tokens: The number of tokens required for the request.
                Defaults to `1`.
        """
        yield  # pragma: no cover
