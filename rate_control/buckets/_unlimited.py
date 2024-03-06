__all__ = [
    'UnlimitedBucket',
]

import sys

from anyio import sleep_forever

from rate_control.buckets._base._abc import Bucket

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class UnlimitedBucket(Bucket):
    """Bucket that allows an unlimited amount of requests"""

    @override
    def can_acquire(self, tokens: float = 1) -> bool:
        return True

    @override
    def acquire(self, tokens: float = 1) -> None:
        """Acquiring tokens from an unlimited bucket has no effect."""

    @override
    async def wait_for_refill(self) -> None:
        await sleep_forever()
