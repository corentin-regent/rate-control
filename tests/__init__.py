__all__ = [
    'assert_not_raises',
]

import sys
from collections.abc import Iterator
from contextlib import contextmanager

from anyio.lowlevel import checkpoint


@contextmanager
def assert_not_raises() -> Iterator[None]:
    yield


async def checkpoints(repeat: int) -> None:
    for _ in range(repeat):
        await checkpoint()
