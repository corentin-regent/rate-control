__all__ = [
    'FixedWindowCounter',
]

import sys
from typing import Any

from rate_control._buckets._base import BaseWindowedTokenBucket, CapacityUpdatingBucket

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class FixedWindowCounter(BaseWindowedTokenBucket, CapacityUpdatingBucket):
    """Bucket whose refill strategy follows the fixed window counter algorithm.

    The bucket refills once every ``duration`` seconds, to cap its tokens back to ``capacity``.
    """

    def __init__(self, capacity: float, duration: float, **kwargs: Any) -> None:
        super().__init__(capacity, duration, **kwargs)
        self._scheduled_refill = False

    @override
    def _should_schedule_refill(self) -> bool:
        if self._scheduled_refill:
            return False
        self._scheduled_refill = True
        return True

    @override
    def _refill(self, tokens: float) -> None:
        self._tokens = self._capacity
        self._scheduled_refill = False
