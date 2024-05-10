__all__ = [
    'SlidingWindowLog',
]

import sys

from rate_control._buckets._base import BaseWindowedTokenBucket, CapacityUpdatingBucket

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class SlidingWindowLog(BaseWindowedTokenBucket, CapacityUpdatingBucket):
    """Bucket whose refill strategy follows the sliding window log algorithm.

    Every consumed tokens get replenished after ``duration`` seconds.
    """

    @override
    def _should_schedule_refill(self) -> bool:
        return True

    @override
    def _refill(self, tokens: float) -> None:
        self._tokens += tokens
