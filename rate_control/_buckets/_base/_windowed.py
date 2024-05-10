__all__ = [
    'BaseWindowedTokenBucket',
]

import sys
from abc import ABC
from typing import Any

from rate_control._buckets._base._base_rate import BaseRateBucket
from rate_control._helpers import mk_repr

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class BaseWindowedTokenBucket(BaseRateBucket, ABC):
    """Base class for token buckets that follow strategies based on time windows."""

    def __init__(self, capacity: float, duration: float, **kwargs: Any) -> None:
        """
        Args:
            capacity: The number of tokens that can be acquired within ``duration``.
            duration: The window duration in seconds.
        """
        super().__init__(capacity, duration, **kwargs)

    @property
    def _duration(self) -> float:
        return self._delay

    @override
    def __repr__(self) -> str:
        return mk_repr(self, capacity=self._capacity, duration=self._duration)
