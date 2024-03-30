import sys
from math import floor

import pytest
from aiofastforward import FastForward
from anyio.abc import TaskGroup
from anyio.lowlevel import checkpoint

from rate_control import RateLimit
from rate_control.buckets import SlidingWindowLog
from tests import assert_not_raises, checkpoints

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator


@pytest.fixture
async def bucket(capacity: float, duration: float) -> AsyncIterator[SlidingWindowLog]:
    async with SlidingWindowLog(capacity, duration) as _bucket:
        yield _bucket


@pytest.fixture
async def int_capacity_bucket(int_capacity: int, duration: float) -> AsyncIterator[SlidingWindowLog]:
    async with SlidingWindowLog(int_capacity, duration) as _bucket:
        yield _bucket


@pytest.mark.anyio
async def test_argument_validation(
    some_negative_value: float, some_valid_capacity: float, some_valid_duration: float
) -> None:
    with pytest.raises(ValueError):
        SlidingWindowLog(capacity=some_negative_value, duration=some_valid_duration)
    with pytest.raises(ValueError):
        SlidingWindowLog(capacity=0, duration=some_valid_duration)
    with pytest.raises(ValueError):
        SlidingWindowLog(capacity=some_valid_capacity, duration=some_negative_value)
    with pytest.raises(ValueError):
        SlidingWindowLog(capacity=some_valid_capacity, duration=0)
    with assert_not_raises():
        SlidingWindowLog(capacity=some_valid_capacity, duration=some_valid_duration)


@pytest.mark.anyio
async def test_acquire_validation(bucket: SlidingWindowLog, some_negative_value: float) -> None:
    with pytest.raises(ValueError):
        bucket.can_acquire(some_negative_value)
    with pytest.raises(ValueError):
        bucket.acquire(some_negative_value)


@pytest.mark.anyio
async def test_token_consumption(bucket: SlidingWindowLog, capacity: float, any_token: float) -> None:
    assert bucket.can_acquire(capacity)
    bucket.acquire(capacity)
    assert not bucket.can_acquire(any_token)
    with pytest.raises(RateLimit):
        bucket.acquire(any_token)


@pytest.mark.anyio
async def test_multiple_consumptions_with_float_capacity(bucket: SlidingWindowLog, capacity: float) -> None:
    for _ in range(floor(capacity)):
        assert bucket.can_acquire(1)
        bucket.acquire(1)
    assert not bucket.can_acquire(1)


@pytest.mark.anyio
async def test_multiple_consumptions_with_int_capacity(
    int_capacity_bucket: SlidingWindowLog, int_capacity: int, any_token: float
) -> None:
    for _ in range(int_capacity):
        assert int_capacity_bucket.can_acquire(1)
        int_capacity_bucket.acquire(1)
    assert not int_capacity_bucket.can_acquire(any_token)


@pytest.mark.anyio
async def test_refill(
    bucket: SlidingWindowLog, capacity: float, duration: float, some_positive_int: int, fast_forward: FastForward
) -> None:
    for _ in range(some_positive_int):
        bucket.acquire(capacity)
        assert not bucket.can_acquire(capacity)
        await fast_forward(duration)
        assert bucket.can_acquire(capacity)


@pytest.mark.anyio
async def test_refill_delay(
    bucket: SlidingWindowLog,
    capacity: float,
    duration: float,
    any_token: float,
    fast_forward: FastForward,
    tiny_delay: float,
) -> None:
    bucket.acquire(capacity / 2)
    await fast_forward(duration / 2)
    bucket.acquire(capacity / 2)

    await checkpoint()
    await fast_forward(duration / 2 - tiny_delay)
    assert not bucket.can_acquire(any_token)
    await fast_forward(tiny_delay)
    await checkpoint()
    assert bucket.can_acquire(capacity / 2)
    assert not bucket.can_acquire(capacity / 2 + any_token)

    await fast_forward(duration / 2)
    await checkpoint()
    assert bucket.can_acquire(capacity)


@pytest.mark.anyio
async def test_wait_for_refill(
    bucket: SlidingWindowLog,
    duration: float,
    any_token: float,
    fast_forward: FastForward,
    tiny_delay: float,
    task_group: TaskGroup,
) -> None:
    refilled = 0

    async def wait_for_refill() -> None:
        await bucket.wait_for_refill()
        nonlocal refilled
        refilled += 1

    bucket.acquire(any_token)
    task_group.start_soon(wait_for_refill)
    await fast_forward(duration / 2)
    bucket.acquire(any_token)
    await checkpoint()

    await fast_forward(duration / 2 - tiny_delay)
    await checkpoints(2)
    assert not refilled
    await fast_forward(tiny_delay)
    await checkpoints(2)
    assert refilled == 1
    task_group.start_soon(wait_for_refill)

    await fast_forward(duration / 2)
    await checkpoints(2)
    assert refilled == 2


@pytest.mark.anyio
async def test_update_capacity(
    bucket: SlidingWindowLog,
    capacity: float,
    duration: float,
    any_token: float,
    fast_forward: FastForward,
) -> None:
    lower_capacity = capacity / 2
    assert bucket.can_acquire(capacity)
    bucket.acquire(capacity)

    bucket.update_capacity(lower_capacity)
    assert not bucket.can_acquire(any_token)
    await fast_forward(duration)
    assert bucket.can_acquire(lower_capacity)
    assert not bucket.can_acquire(capacity)

    bucket.update_capacity(capacity)
    assert bucket.can_acquire(capacity)


@pytest.mark.anyio
async def test_update_capacity_validation(
    bucket: SlidingWindowLog, some_negative_value: float, some_valid_capacity: float
) -> None:
    with pytest.raises(ValueError):
        bucket.update_capacity(0)
    with pytest.raises(ValueError):
        bucket.update_capacity(some_negative_value)
    with assert_not_raises():
        bucket.update_capacity(some_valid_capacity)


def test_not_entering_context(capacity: float, duration: float, any_token: float) -> None:
    bucket = SlidingWindowLog(capacity, duration)
    with pytest.raises(RuntimeError):
        bucket.acquire(any_token)


@pytest.mark.anyio
async def test_repr(bucket: SlidingWindowLog, capacity: float, duration: float) -> None:
    assert repr(bucket) == f'SlidingWindowLog({capacity=}, {duration=})'
