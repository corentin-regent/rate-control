import math
import sys
from typing import Any

import pytest
from aiofastforward import FastForward
from anyio.abc import TaskGroup
from anyio.lowlevel import checkpoint

from rate_control.buckets import UnlimitedBucket
from tests import assert_not_raises

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator


@pytest.fixture
async def bucket() -> AsyncIterator[UnlimitedBucket]:
    async with UnlimitedBucket() as _bucket:
        yield _bucket


@pytest.mark.anyio
async def test_acquire(bucket: UnlimitedBucket) -> None:
    assert bucket.can_acquire(math.inf)
    with assert_not_raises():
        bucket.acquire(math.inf)


@pytest.mark.anyio
async def test_wait_for_refill(
    bucket: UnlimitedBucket, any_token: float, aeons: float, task_group: TaskGroup, fast_forward: FastForward
) -> None:
    refilled = False

    async def wait_for_refill(**_: Any) -> None:
        await bucket.wait_for_refill()
        nonlocal refilled
        refilled = True  # pragma: no cover

    bucket.acquire(any_token)
    task_group.start_soon(wait_for_refill)
    await checkpoint()
    assert not refilled
    await fast_forward(aeons)
    assert not refilled


@pytest.mark.anyio
async def test_repr(bucket: UnlimitedBucket) -> None:
    assert repr(bucket) == 'UnlimitedBucket()'
