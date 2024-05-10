__all__ = [
    'NoopController',
]

import sys
from contextlib import asynccontextmanager
from typing import Any, ClassVar, Literal

from rate_control._controllers._abc import RateController
from rate_control._helpers import mk_repr

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class NoopController(RateController):
    """Rate controller that accepts all requests and does nothing."""

    _instance: ClassVar['NoopController']

    def __new__(cls, *_: Any, **kwargs: Any) -> 'NoopController':
        """
        Positional arguments, accepted for consistency with other rate controllers, are ignored.
        Keyword arguments are passed to the super class constructor.

        Note:
            Implementation detail: The ``__new__`` method returns
            a singleton instance, for better memory management.
        """
        try:
            return cls._instance
        except AttributeError:
            cls._instance = super().__new__(cls, **kwargs)
            return cls._instance

    @override
    def __repr__(self) -> str:
        return mk_repr(self)

    @override
    def can_acquire(self, tokens: float = 1) -> Literal[True]:
        """Always returns `True`."""
        return True

    @override
    @asynccontextmanager
    async def request(self, tokens: float = 1, **_: Any) -> AsyncIterator[None]:
        """Asynchronous context manager that does nothing else than yield."""
        yield
