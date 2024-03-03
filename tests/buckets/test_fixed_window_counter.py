import sys
from math import floor

import pytest
from aiofastforward import FastForward
from anyio.abc import TaskGroup
from anyio.lowlevel import checkpoint

from rate_control import RateLimit
from rate_control.buckets import FixedWindowCounter
from tests import assert_not_raises, checkpoints

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator
else:
    from typing import AsyncIterator


@pytest.fixture
async def int_capacity_bucket(int_capacity: int, duration: float) -> AsyncIterator[FixedWindowCounter]:
    async with FixedWindowCounter(int_capacity, duration) as _bucket:
        yield _bucket


@pytest.mark.anyio
async def test_argument_validation(
    some_negative_value: float, some_valid_capacity: float, some_valid_duration: float
) -> None:
    with pytest.raises(ValueError):
        FixedWindowCounter(capacity=some_negative_value, duration=some_valid_duration)
    with pytest.raises(ValueError):
        FixedWindowCounter(capacity=0, duration=some_valid_duration)
    with pytest.raises(ValueError):
        FixedWindowCounter(capacity=some_valid_capacity, duration=some_negative_value)
    with pytest.raises(ValueError):
        FixedWindowCounter(capacity=some_valid_capacity, duration=0)
    with assert_not_raises():
        FixedWindowCounter(capacity=some_valid_capacity, duration=some_valid_duration)


@pytest.mark.anyio
async def test_acquire_validation(fixed_window_counter: FixedWindowCounter, some_negative_value: float) -> None:
    with pytest.raises(ValueError):
        fixed_window_counter.can_acquire(some_negative_value)
    with pytest.raises(ValueError):
        fixed_window_counter.acquire(some_negative_value)


@pytest.mark.anyio
async def test_token_consumption(fixed_window_counter: FixedWindowCounter, capacity: float, any_token: float) -> None:
    assert fixed_window_counter.can_acquire(capacity)
    fixed_window_counter.acquire(capacity)
    assert not fixed_window_counter.can_acquire(any_token)
    with pytest.raises(RateLimit):
        fixed_window_counter.acquire(any_token)


@pytest.mark.anyio
async def test_multiple_consumptions_with_float_capacity(
    fixed_window_counter: FixedWindowCounter, capacity: float
) -> None:
    for _ in range(floor(capacity)):
        assert fixed_window_counter.can_acquire(1)
        fixed_window_counter.acquire(1)
    assert not fixed_window_counter.can_acquire(1)


@pytest.mark.anyio
async def test_multiple_consumptions_with_int_capacity(
    int_capacity_bucket: FixedWindowCounter, int_capacity: int, any_token: float
) -> None:
    for _ in range(int_capacity):
        assert int_capacity_bucket.can_acquire(1)
        int_capacity_bucket.acquire(1)
    assert not int_capacity_bucket.can_acquire(any_token)


@pytest.mark.anyio
async def test_refill(
    fixed_window_counter: FixedWindowCounter,
    capacity: float,
    duration: float,
    some_positive_int: int,
    fast_forward: FastForward,
) -> None:
    for _ in range(some_positive_int):
        fixed_window_counter.acquire(capacity)
        assert not fixed_window_counter.can_acquire(capacity)
        await fast_forward(duration)
        assert fixed_window_counter.can_acquire(capacity)


@pytest.mark.anyio
async def test_refill_delay(
    fixed_window_counter: FixedWindowCounter,
    capacity: float,
    duration: float,
    any_token: float,
    fast_forward: FastForward,
    tiny_delay: float,
) -> None:
    fixed_window_counter.acquire(capacity)
    await fast_forward(duration - tiny_delay)
    await checkpoint()
    assert not fixed_window_counter.can_acquire(any_token)
    await fast_forward(tiny_delay)
    await checkpoint()
    assert fixed_window_counter.can_acquire(capacity)


@pytest.mark.anyio
async def test_wait_for_refill(
    fixed_window_counter: FixedWindowCounter,
    duration: float,
    any_token: float,
    fast_forward: FastForward,
    tiny_delay: float,
    task_group: TaskGroup,
) -> None:
    refilled = False

    async def wait_for_refill() -> None:
        await fixed_window_counter.wait_for_refill()
        nonlocal refilled
        refilled = True

    fixed_window_counter.acquire(any_token)
    task_group.start_soon(wait_for_refill)
    await fast_forward(duration - tiny_delay)
    await checkpoints(2)
    assert not refilled
    await fast_forward(tiny_delay)
    await checkpoints(2)
    assert refilled


def test_not_entering_context(capacity: float, duration: float, any_token: float) -> None:
    bucket = FixedWindowCounter(capacity, duration)
    with pytest.raises(RuntimeError):
        bucket.acquire(any_token)


@pytest.mark.anyio
async def test_repr(fixed_window_counter: FixedWindowCounter, capacity: float, duration: float) -> None:
    assert repr(fixed_window_counter) == f'FixedWindowCounter({capacity=}, {duration=})'
