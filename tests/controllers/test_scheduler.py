import sys
from contextlib import AsyncExitStack
from functools import partial
from typing import Any
from unittest.mock import Mock

import pytest
from aiofastforward import FastForward
from anyio import create_task_group
from anyio.abc import TaskGroup
from anyio.lowlevel import checkpoint

from rate_control import Bucket, Priority, RateLimit, ReachedMaxPending, Scheduler
from tests import assert_not_raises, checkpoints

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Awaitable, Callable

    Tuple = tuple
else:
    from typing import AsyncIterator, Awaitable, Callable, Tuple


class _Called:
    def __init__(self) -> None:
        self.value = False

    def __bool__(self) -> bool:
        return self.value


@pytest.fixture
def mocked_window_counter(fixed_window_counter: Bucket) -> Mock:
    mock = Mock(wraps=fixed_window_counter)
    mock.acquire = Mock(wraps=fixed_window_counter.acquire)
    return mock


@pytest.fixture
async def scheduler(mocked_window_counter: Mock, max_concurrency: int, max_pending: int) -> AsyncIterator[Scheduler]:
    async with Scheduler(mocked_window_counter, max_concurrency=max_concurrency, max_pending=max_pending) as _scheduler:
        yield _scheduler


@pytest.fixture
async def mocked_scheduler(mock_bucket: Mock, max_concurrency: int, max_pending: int) -> AsyncIterator[Scheduler]:
    async with Scheduler(mock_bucket, max_concurrency=max_concurrency, max_pending=max_pending) as _scheduler:
        yield _scheduler


def _prepare_request(scheduler: Scheduler) -> Tuple[Callable[..., Awaitable[None]], _Called]:
    called = _Called()

    async def schedule(*args: Any) -> None:
        async with scheduler.schedule(*args):
            called.value = True

    return schedule, called


@pytest.mark.anyio
async def test_argument_validation(mock_bucket: Bucket, some_negative_int: int, some_positive_int: int) -> None:
    mk_scheduler = partial(Scheduler, mock_bucket)
    with assert_not_raises():
        mk_scheduler()

    with pytest.raises(ValueError):
        mk_scheduler(max_concurrency=0)
    with pytest.raises(ValueError):
        mk_scheduler(max_concurrency=some_negative_int)
    with assert_not_raises():
        mk_scheduler(max_concurrency=None)
    with assert_not_raises():
        mk_scheduler(max_concurrency=some_positive_int)

    with pytest.raises(ValueError):
        mk_scheduler(max_pending=0)
    with pytest.raises(ValueError):
        mk_scheduler(max_pending=some_negative_int)
    with assert_not_raises():
        mk_scheduler(max_pending=None)
    with assert_not_raises():
        mk_scheduler(max_pending=some_positive_int)


@pytest.mark.anyio
async def test_simple_scheduling(
    scheduler: Scheduler,
    mocked_window_counter: Mock,
    capacity: float,
    duration: float,
    any_token: float,
    task_group: TaskGroup,
    fast_forward: FastForward,
) -> None:
    assert scheduler.can_acquire(capacity)
    assert not scheduler.can_acquire(capacity + any_token)
    schedule_draw, draw_called = _prepare_request(scheduler)
    schedule_other, other_called = _prepare_request(scheduler)
    task_group.start_soon(schedule_draw, capacity)
    task_group.start_soon(schedule_other, any_token)

    await checkpoints(4)
    assert draw_called
    assert not other_called
    mocked_window_counter.acquire.assert_called_once_with(capacity)
    mocked_window_counter.acquire.reset_mock()

    await fast_forward(duration)
    await checkpoints(3)
    assert other_called
    mocked_window_counter.acquire.assert_called_once_with(any_token)


@pytest.mark.anyio
async def test_request_priority(
    scheduler: Scheduler,
    capacity: float,
    duration: float,
    task_group: TaskGroup,
    fast_forward: FastForward,
) -> None:
    schedule_draw, draw_called = _prepare_request(scheduler)
    schedule_low_priority, low_priority_called = _prepare_request(scheduler)
    schedule_high_priority, high_priority_called = _prepare_request(scheduler)
    task_group.start_soon(schedule_draw, capacity)
    task_group.start_soon(schedule_low_priority, capacity, Priority.LOW)
    task_group.start_soon(schedule_high_priority, capacity, Priority.HIGH)

    await checkpoints(2)
    assert draw_called

    await fast_forward(duration)
    await checkpoints(3)
    assert high_priority_called
    assert not low_priority_called

    await fast_forward(duration)
    await checkpoints(2)
    assert low_priority_called


@pytest.mark.anyio
async def test_max_concurrency(
    mocked_scheduler: Scheduler,
    mock_bucket: Mock,
    max_concurrency: int,
    task_group: TaskGroup,
) -> None:
    mock_bucket.can_acquire = Mock(return_value=True)
    async with AsyncExitStack() as stack:
        for _ in range(max_concurrency - 1):
            assert mocked_scheduler.can_acquire()
            await stack.enter_async_context(mocked_scheduler.schedule())

        schedule_additional, additional_called = _prepare_request(mocked_scheduler)
        assert mocked_scheduler.can_acquire()
        async with mocked_scheduler.schedule():
            assert not mocked_scheduler.can_acquire()
            task_group.start_soon(schedule_additional)
            await checkpoints(2)
            assert not additional_called
        await checkpoints(2)
        assert additional_called


@pytest.mark.anyio
async def test_max_pending(
    mocked_scheduler: Scheduler,
    mock_bucket: Mock,
    max_pending: int,
    task_group: TaskGroup,
) -> None:
    mock_bucket.can_acquire = Mock(return_value=False)
    for _ in range(max_pending):
        schedule, _ = _prepare_request(mocked_scheduler)
        task_group.start_soon(schedule)
    await checkpoint()

    with pytest.raises(ReachedMaxPending):
        await mocked_scheduler.schedule().__aenter__()


@pytest.mark.anyio
async def test_fill_or_kill(mocked_scheduler: Scheduler, mock_bucket: Mock) -> None:
    mock_bucket.can_acquire = Mock(return_value=False)
    with pytest.raises(RateLimit):
        await mocked_scheduler.schedule(fill_or_kill=True).__aenter__()


@pytest.mark.anyio
async def test_cancel_pending_task(
    scheduler: Scheduler,
    capacity: float,
    duration: float,
    task_group: TaskGroup,
    fast_forward: FastForward,
) -> None:
    await scheduler.schedule(cost=capacity).__aenter__()
    schedule_to_cancel, to_cancel_called = _prepare_request(scheduler)
    schedule_other, other_called = _prepare_request(scheduler)

    async with create_task_group() as other_task_group:
        other_task_group.start_soon(schedule_to_cancel, capacity, Priority.HIGH)
        task_group.start_soon(schedule_other, capacity, Priority.LOW)
        await checkpoints(4)
        other_task_group.cancel_scope.cancel()

    await fast_forward(duration)
    await checkpoints(3)
    assert not to_cancel_called
    assert other_called


@pytest.mark.anyio
async def test_not_entering_context(mock_bucket: Bucket) -> None:
    bucket = Scheduler(mock_bucket)
    with pytest.raises(RuntimeError):
        await bucket.schedule().__aenter__()


@pytest.mark.anyio
async def test_repr(mock_bucket: Mock, max_concurrency: int, max_pending: int) -> None:
    scheduler = Scheduler(mock_bucket, max_concurrency=max_concurrency, max_pending=max_pending)
    assert repr(scheduler) == f'Scheduler(bucket={mock_bucket!r}, {max_concurrency=}, {max_pending=})'
