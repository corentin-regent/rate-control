__all__ = [
    'TokenBasedBucket',
]

import sys
from abc import ABC
from typing import Any

from rate_control._buckets._base._abc import Bucket
from rate_control._helpers._validation import validate_capacity, validate_tokens

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class TokenBasedBucket(Bucket, ABC):
    """Base class for buckets that monitor the requests using tokens."""

    def __init__(self, capacity: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        validate_capacity(capacity)
        self._tokens = self._capacity = capacity

    @override
    def can_acquire(self, tokens: float) -> bool:
        validate_tokens(tokens)
        return tokens <= self._tokens

    @override
    def acquire(self, tokens: float) -> None:
        self._assert_can_acquire(tokens)
        self._tokens -= tokens
