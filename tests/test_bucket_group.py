import sys
from unittest.mock import Mock

import pytest
from aiofastforward import FastForward
from anyio import Event, sleep_forever
from anyio.abc import TaskGroup

from rate_control import Bucket, BucketGroup, RateLimit
from tests import checkpoints

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Collection, Iterable
else:
    from typing import AsyncIterator, Collection, Iterable


@pytest.fixture
async def mocked_bucket_group(mock_buckets: Iterable[Mock]) -> AsyncIterator[BucketGroup]:
    async with BucketGroup(*mock_buckets, should_enter_context=False) as bucket_group:
        yield bucket_group


@pytest.mark.anyio
async def test_entering_buckets_context(mock_buckets: Collection[Mock]) -> None:
    async with BucketGroup(*mock_buckets, should_enter_context=True):
        for bucket in mock_buckets:
            bucket.__aenter__.assert_awaited_once()
    for bucket in mock_buckets:
        bucket.__aexit__.assert_awaited_once()


@pytest.mark.anyio
async def test_not_entering_buckets_context(mock_buckets: Collection[Mock]) -> None:
    async with BucketGroup(*mock_buckets, should_enter_context=False):
        for bucket in mock_buckets:
            bucket.__aenter__.assert_not_called()
    for bucket in mock_buckets:
        bucket.__aexit__.assert_not_called()


@pytest.mark.anyio
async def test_acquire(
    mocked_bucket_group: BucketGroup,
    mock_buckets: Collection[Mock],
    mock_bucket: Mock,
    some_tokens: float,
    any_token: float,
) -> None:
    for bucket in mock_buckets:
        bucket.can_acquire = Mock(return_value=True)
    mock_bucket.can_acquire = lambda tokens: tokens <= some_tokens

    assert mocked_bucket_group.can_acquire(some_tokens)
    assert not mocked_bucket_group.can_acquire(some_tokens + any_token)

    with pytest.raises(RateLimit):
        mocked_bucket_group.acquire(some_tokens + any_token)
    for bucket in mock_buckets:
        bucket.acquire.assert_not_called()

    mocked_bucket_group.acquire(some_tokens)
    for bucket in mock_buckets:
        bucket.acquire.assert_called_once_with(some_tokens)


@pytest.mark.anyio
async def test_wait_for_refill(
    mocked_bucket_group: BucketGroup,
    mock_buckets: Collection[Mock],
    mock_bucket: Mock,
    fast_forward: FastForward,
    task_group: TaskGroup,
    aeons: float,
) -> None:
    refill_event = Event()
    for bucket in mock_buckets:
        bucket.wait_for_refill = sleep_forever
    mock_bucket.wait_for_refill = refill_event.wait

    refilled = False

    async def wait_for_refill() -> None:
        await mocked_bucket_group.wait_for_refill()
        nonlocal refilled
        refilled = True

    task_group.start_soon(wait_for_refill)
    await fast_forward(aeons)
    assert not refilled
    refill_event.set()
    await checkpoints(3)
    assert refilled


@pytest.mark.anyio
async def test_iter(mocked_bucket_group: BucketGroup, mock_buckets: Collection[Mock]) -> None:
    assert set(mocked_bucket_group) == set(mock_buckets)
    assert len(set(mocked_bucket_group)) == len(mock_buckets)


@pytest.mark.anyio
async def test_repr(mock_bucket: Mock, fixed_window_counter: Bucket, should_enter_context: bool) -> None:
    bucket_group = BucketGroup(mock_bucket, fixed_window_counter, should_enter_context=should_enter_context)
    assert repr(bucket_group) == f'BucketGroup({mock_bucket!r}, {fixed_window_counter!r}, {should_enter_context=})'
