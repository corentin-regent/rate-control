__all__ = [
    'CapacityUpdatingBucket',
]

from rate_control._buckets._base._token_based import TokenBasedBucket
from rate_control._helpers._validation import validate_capacity


class CapacityUpdatingBucket(TokenBasedBucket):
    """Mixin for buckets which token capacity can be updated."""

    def update_capacity(self, new_capacity: float) -> None:
        """Update the bucket's token capacity.

        Changes take effect instantly, and the amount of remaining tokens is updated accordingly.

        Args:
            new_capacity: The new token capacity of the bucket.
        """
        validate_capacity(new_capacity)
        self._tokens += new_capacity - self._capacity
        self._capacity = new_capacity
