import sys
from contextlib import AsyncExitStack
from unittest.mock import Mock

import pytest

from rate_control import Bucket, RateLimit, RateLimiter
from tests import assert_not_raises

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Collection
else:
    from typing import AsyncIterator, Collection


@pytest.fixture
async def rate_limiter(mock_bucket: Mock, max_concurrency: int) -> AsyncIterator[RateLimiter]:
    async with RateLimiter(mock_bucket, max_concurrency=max_concurrency) as rate_limiter:
        yield rate_limiter


@pytest.fixture
async def rate_limiter_without_bucket(max_concurrency: int) -> AsyncIterator[RateLimiter]:
    async with RateLimiter(max_concurrency=max_concurrency) as rate_limiter:
        yield rate_limiter


@pytest.mark.anyio
async def test_argument_validation(some_negative_int: int, some_positive_int: int) -> None:
    with assert_not_raises():
        RateLimiter()

    with pytest.raises(ValueError):
        RateLimiter(max_concurrency=0)
    with pytest.raises(ValueError):
        RateLimiter(max_concurrency=some_negative_int)
    with assert_not_raises():
        RateLimiter(max_concurrency=None)
    with assert_not_raises():
        RateLimiter(max_concurrency=some_positive_int)


@pytest.mark.anyio
async def test_simple_rate_limiting(
    rate_limiter: RateLimiter, mock_bucket: Mock, some_tokens: float, any_token: float
) -> None:
    mock_bucket.can_acquire = lambda tokens: tokens <= some_tokens

    assert rate_limiter.can_acquire(some_tokens)
    assert not rate_limiter.can_acquire(some_tokens + any_token)
    with pytest.raises(RateLimit):
        async with rate_limiter.request(some_tokens + any_token):
            ...
    mock_bucket.acquire.assert_not_called()

    async with rate_limiter.request(some_tokens):
        mock_bucket.acquire.assert_called_once_with(some_tokens)


@pytest.mark.anyio
async def test_max_concurrency(rate_limiter_without_bucket: RateLimiter, max_concurrency: int) -> None:
    async with AsyncExitStack() as stack:
        for _ in range(max_concurrency - 1):
            assert rate_limiter_without_bucket.can_acquire()
            await stack.enter_async_context(rate_limiter_without_bucket.request())

        async with rate_limiter_without_bucket.request():
            assert not rate_limiter_without_bucket.can_acquire()
            with pytest.raises(RateLimit):
                async with rate_limiter_without_bucket.request():
                    ...

        assert rate_limiter_without_bucket.can_acquire()
        with assert_not_raises():
            async with rate_limiter_without_bucket.request():
                ...


@pytest.mark.anyio
async def test_multiple_buckets(mock_buckets: Collection[Mock], any_token: float) -> None:
    async with RateLimiter(*mock_buckets, should_enter_context=False) as rate_limiter, rate_limiter.request(any_token):
        for bucket in mock_buckets:
            bucket.acquire.assert_called_once_with(any_token)


@pytest.mark.anyio
async def test_entering_buckets_context(mock_buckets: Collection[Mock]) -> None:
    async with RateLimiter(*mock_buckets, should_enter_context=True):
        for bucket in mock_buckets:
            bucket.__aenter__.assert_awaited_once()
    for bucket in mock_buckets:
        bucket.__aexit__.assert_awaited_once()


@pytest.mark.anyio
async def test_not_entering_buckets_context(mock_buckets: Collection[Mock]) -> None:
    async with RateLimiter(*mock_buckets, should_enter_context=False):
        for bucket in mock_buckets:
            bucket.__aenter__.assert_not_called()
    for bucket in mock_buckets:
        bucket.__aexit__.assert_not_called()


@pytest.mark.anyio
async def test_entering_context_multiple_times(fixed_window_counter: Bucket, capacity: float, any_token: float) -> None:
    async with RateLimiter(fixed_window_counter, should_enter_context=False) as rate_limiter:
        async with rate_limiter.request(capacity / 2):
            pass

        async with rate_limiter:
            assert rate_limiter.can_acquire(capacity / 2)
            async with rate_limiter.request(capacity / 2):
                pass

        async with rate_limiter:
            assert not rate_limiter.can_acquire(any_token)
            with pytest.raises(RateLimit):
                async with rate_limiter.request(any_token):
                    ...


@pytest.mark.anyio
async def test_repr(mock_bucket: Bucket, max_concurrency: int, should_enter_context: bool) -> None:
    scheduler = RateLimiter(mock_bucket, should_enter_context=should_enter_context, max_concurrency=max_concurrency)
    assert repr(scheduler) == f'RateLimiter({mock_bucket!r}, {should_enter_context=}, {max_concurrency=})'


@pytest.mark.anyio
async def test_repr_without_bucket(max_concurrency: int, should_enter_context: bool) -> None:
    scheduler = RateLimiter(max_concurrency=max_concurrency, should_enter_context=should_enter_context)
    assert repr(scheduler) == f'RateLimiter({max_concurrency=})'
