__all__ = [
    'LeakyBucket',
]

import math
import sys
from typing import Any

from rate_control._buckets._base import BaseRateBucket
from rate_control._errors import RateLimit
from rate_control._helpers import mk_repr

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class LeakyBucket(BaseRateBucket):
    """Bucket whose refill strategy follows the leaky bucket algorithm.

    Only one request can get executed every ``delay`` seconds.
    """

    def __init__(self, delay: float, **kwargs: Any) -> None:
        """
        Args:
            delay: The delay before a new request can pass through.
        """
        super().__init__(capacity=math.inf, delay=delay, **kwargs)
        self._can_pass_through = True

    @override
    def __repr__(self) -> str:
        return mk_repr(self, delay=self._delay)

    @override
    def can_acquire(self, tokens: float = 1) -> bool:
        return self._can_pass_through

    @override
    def acquire(self, tokens: float = 1) -> None:
        if not self._can_pass_through:
            raise RateLimit
        self._can_pass_through = False
        self._ensure_refill()

    @override
    def _should_schedule_refill(self) -> bool:
        return True

    @override
    def _refill(self, tokens: float) -> None:
        self._can_pass_through = True
