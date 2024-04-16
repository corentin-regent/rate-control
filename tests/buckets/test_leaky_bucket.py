import sys

import pytest
from aiofastforward import FastForward
from anyio.abc import TaskGroup
from anyio.lowlevel import checkpoint

from rate_control import RateLimit
from rate_control._buckets import LeakyBucket
from tests import assert_not_raises, checkpoints

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator


@pytest.fixture
async def bucket(delay: float) -> AsyncIterator[LeakyBucket]:
    async with LeakyBucket(delay) as _bucket:
        yield _bucket


@pytest.mark.anyio
async def test_argument_validation(some_negative_value: float, some_valid_delay: float) -> None:
    with pytest.raises(ValueError):
        LeakyBucket(delay=some_negative_value)
    with pytest.raises(ValueError):
        LeakyBucket(delay=0)
    with assert_not_raises():
        LeakyBucket(delay=some_valid_delay)


@pytest.mark.anyio
async def test_consumption(bucket: LeakyBucket) -> None:
    assert bucket.can_acquire()
    bucket.acquire()
    assert not bucket.can_acquire()
    with pytest.raises(RateLimit):
        bucket.acquire()


@pytest.mark.anyio
async def test_refill(bucket: LeakyBucket, delay: float, some_positive_int: int, fast_forward: FastForward) -> None:
    for _ in range(some_positive_int):
        bucket.acquire()
        assert not bucket.can_acquire()
        await fast_forward(delay)
        assert bucket.can_acquire()


@pytest.mark.anyio
async def test_refill_delay(bucket: LeakyBucket, delay: float, fast_forward: FastForward, tiny_delay: float) -> None:
    bucket.acquire()
    await fast_forward(delay - tiny_delay)
    assert not bucket.can_acquire()
    await fast_forward(tiny_delay)
    await checkpoint()
    assert bucket.can_acquire()


@pytest.mark.anyio
async def test_wait_for_refill(
    bucket: LeakyBucket, delay: float, fast_forward: FastForward, tiny_delay: float, task_group: TaskGroup
) -> None:
    refilled = False

    async def wait_for_refill() -> None:
        await bucket.wait_for_refill()
        nonlocal refilled
        refilled = True

    bucket.acquire()
    task_group.start_soon(wait_for_refill)
    await fast_forward(delay - tiny_delay)
    await checkpoints(2)
    assert not refilled
    await fast_forward(tiny_delay)
    await checkpoints(2)
    assert refilled


def test_not_entering_context(delay: float) -> None:
    bucket = LeakyBucket(delay)
    with pytest.raises(RuntimeError):
        bucket.acquire()


@pytest.mark.anyio
async def test_repr(bucket: LeakyBucket, delay: float) -> None:
    assert repr(bucket) == f'LeakyBucket({delay=})'
