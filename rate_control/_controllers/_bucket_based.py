__all__ = [
    'BucketBasedRateController',
]

import sys
from abc import ABC
from contextlib import contextmanager
from typing import Any, Optional

from rate_control._bucket_group import BucketGroup
from rate_control._buckets import Bucket
from rate_control._controllers._abc import RateController
from rate_control._errors import RateLimit
from rate_control._helpers import mk_repr
from rate_control._helpers._validation import validate_max_concurrency

if sys.version_info >= (3, 9):
    from collections.abc import Iterator
else:
    from typing import Iterator

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class BucketBasedRateController(RateController, ABC):
    """Mixin for rate controllers that use buckets."""

    def __init__(
        self,
        *buckets: Bucket,
        should_enter_context: bool = True,
        max_concurrency: Optional[int] = None,
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
        """
        super().__init__(**kwargs)
        validate_max_concurrency(max_concurrency)
        self._bucket = (
            None
            if not buckets
            else buckets[0]
            if len(buckets) == 1
            else BucketGroup(*buckets, should_enter_context=should_enter_context)
        )
        self._should_enter_context = should_enter_context
        self._max_concurrency = max_concurrency
        self._concurrent_requests = 0

    @override
    async def __aenter__(self) -> Self:
        """Enter the controller's context.

        Also enters the context of the underlying buckets,
        if the `should_enter_context` flag was set to `True`.
        """
        await super().__aenter__()
        if self._should_enter_context and self._bucket is not None:
            await self._bucket.__aenter__()
        return self

    @override
    async def __aexit__(self, *exc_info: Any) -> Optional[bool]:
        """Exit the controller's context.

        Also exits the context of the underlying buckets,
        if the `should_enter_context` flag was set to `True`.
        """
        if self._should_enter_context and self._bucket is not None:
            await self._bucket.__aexit__(*exc_info)
        return await super().__aexit__(*exc_info)

    @override
    def __repr__(self) -> str:
        return (
            mk_repr(
                self,
                self._bucket,
                should_enter_context=self._should_enter_context,
                max_concurrency=self._max_concurrency,
            )
            if self._bucket is not None
            else mk_repr(self, max_concurrency=self._max_concurrency)
        )

    @override
    def can_acquire(self, tokens: float = 1) -> bool:
        return not self._is_concurrency_limited and (self._bucket is None or self._bucket.can_acquire(tokens))

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
