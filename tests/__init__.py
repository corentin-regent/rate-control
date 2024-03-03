__all__ = [
    'assert_not_raises',
]

import sys
from contextlib import contextmanager

from anyio.lowlevel import checkpoint

if sys.version_info >= (3, 9):
    from collections.abc import Iterator
else:
    from typing import Iterator


@contextmanager
def assert_not_raises() -> Iterator[None]:
    yield


async def checkpoints(repeat: int) -> None:
    for _ in range(repeat):
        await checkpoint()
