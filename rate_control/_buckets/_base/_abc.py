__all__ = [
    'Bucket',
]

import sys
from abc import ABC, abstractmethod
from typing import Any, Optional

from rate_control._errors import RateLimit

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class Bucket(ABC):
    """Abstract base class for buckets."""

    async def __aenter__(self) -> Self:
        """Enter the bucket context.

        It may for example start scheduling replenishments.
        """
        return self

    async def __aexit__(self, *_: Any) -> Optional[bool]:
        """Exit the bucket context.

        It may for example cancel internal background tasks.
        """

    @abstractmethod
    async def wait_for_refill(self) -> None:
        """Wait until some tokens are replenished."""

    @abstractmethod
    def can_acquire(self, tokens: float) -> bool:
        """Whether the given amount of tokens can be acquired.

        Args:
            tokens: The amount of tokens that we want to acquire.

        Returns:
            Whether the given amount of tokens is available to consume.
        """

    @abstractmethod
    def acquire(self, tokens: float) -> None:
        """Acquire the given amount of tokens.

        Args:
            tokens: The amount of tokens to acquire.

        Raises:
            RateLimit: Cannot acquire the given amount of tokens.
        """

    def _assert_can_acquire(self, tokens: float) -> None:
        """Make sure that the given amount of tokens can be acquired.

        Args:
            tokens: The amount of tokens to acquire.

        Raises:
            RateLimit: Cannot acquire the given amount of tokens.
        """
        if not self.can_acquire(tokens):
            raise RateLimit(f'Cannot acquire {tokens} tokens.')
