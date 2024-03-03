from __future__ import annotations

__all__ = [
    'validate_buckets',
    'validate_capacity',
    'validate_delay',
    'validate_max_concurrency',
    'validate_max_pending',
    'validate_tokens',
]

import sys
from typing import TYPE_CHECKING, Optional

if sys.version_info >= (3, 9):
    from collections.abc import Collection
else:
    from typing import Collection

if TYPE_CHECKING:
    from rate_control.buckets._base import Bucket


def validate_buckets(buckets: Collection[Bucket]) -> None:
    """
    Raises:
        ValueError: No bucket was provided.
    """
    if not buckets:
        raise ValueError('At least one token bucket must be provided')


def validate_capacity(capacity: float) -> None:
    """
    Raises:
        ValueError: Negative or zero capacity was provided.
    """
    if capacity <= 0:
        raise ValueError(f'The bucket capacity has to be strictly positive. Received {capacity}')


def validate_delay(delay: float) -> None:
    """
    Raises:
        ValueError: Negative or zero delay was provided.
    """
    if delay <= 0:
        raise ValueError(f'The bucket refill delay has to be strictly positive. Received {delay}')


def validate_max_concurrency(max_concurrency: Optional[int]) -> None:
    """
    Raises:
        ValueError: Negative or zero concurrency limit was provided.
    """
    if max_concurrency is not None and max_concurrency <= 0:
        raise ValueError(
            f"'max_concurrency' must be strictly positive, or '{None}' for unlimited concurrency. Received {max_concurrency}"
        )


def validate_max_pending(max_pending: Optional[int]) -> None:
    """
    Raises:
        ValueError: Negative or zero pending limit was provided.
    """
    if max_pending is not None and max_pending <= 0:
        raise ValueError(
            f"'max_pending' must be strictly positive, or '{None}' for no pending limit. Received {max_pending}"
        )


def validate_tokens(tokens: float) -> None:
    """
    Raises:
        ValueError: Negative amount of tokens was provided.
    """
    if tokens < 0:
        raise ValueError(f'Cannot acquire a negative amount of tokens. Received {tokens}')
