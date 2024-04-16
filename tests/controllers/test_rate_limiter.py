import sys
from contextlib import AsyncExitStack
from functools import partial
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


@pytest.mark.anyio
async def test_argument_validation(mock_bucket: Mock, some_negative_int: int, some_positive_int: int) -> None:
    mk_rate_limiter = partial(RateLimiter, mock_bucket)
    with assert_not_raises():
        mk_rate_limiter()

    with pytest.raises(ValueError):
        mk_rate_limiter(max_concurrency=0)
    with pytest.raises(ValueError):
        mk_rate_limiter(max_concurrency=some_negative_int)
    with assert_not_raises():
        mk_rate_limiter(max_concurrency=None)
    with assert_not_raises():
        mk_rate_limiter(max_concurrency=some_positive_int)


@pytest.mark.anyio
async def test_simple_rate_limiting(
    rate_limiter: RateLimiter, mock_bucket: Mock, some_tokens: float, any_token: float
) -> None:
    def can_acquire(tokens: float) -> bool:
        return tokens <= some_tokens

    mock_bucket.can_acquire = can_acquire

    assert rate_limiter.can_acquire(some_tokens)
    assert not rate_limiter.can_acquire(some_tokens + any_token)
    with pytest.raises(RateLimit):
        async with rate_limiter.request(some_tokens + any_token):
            ...
    mock_bucket.acquire.assert_not_called()

    async with rate_limiter.request(some_tokens):
        mock_bucket.acquire.assert_called_once_with(some_tokens)


@pytest.mark.anyio
async def test_max_concurrency(rate_limiter: RateLimiter, mock_bucket: Mock, max_concurrency: int) -> None:
    mock_bucket.can_acquire = Mock(return_value=True)
    async with AsyncExitStack() as stack:
        for _ in range(max_concurrency - 1):
            assert rate_limiter.can_acquire()
            await stack.enter_async_context(rate_limiter.request())

        async with rate_limiter.request():
            assert not rate_limiter.can_acquire()
            with pytest.raises(RateLimit):
                async with rate_limiter.request():
                    ...

        assert rate_limiter.can_acquire()
        with assert_not_raises():
            async with rate_limiter.request():
                ...


@pytest.mark.anyio
async def test_multiple_buckets(mock_buckets: Collection[Mock], any_token: float) -> None:
    async with RateLimiter(*mock_buckets, should_enter_context=False) as rate_limiter, rate_limiter.request(any_token):
        for bucket in mock_buckets:
            bucket.acquire.assert_called_once_with(any_token)


@pytest.mark.anyio
async def test_enter_buckets_context(mock_buckets: Collection[Mock]) -> None:
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
async def test_repr(mock_bucket: Bucket, max_concurrency: int) -> None:
    scheduler = RateLimiter(mock_bucket, should_enter_context=False, max_concurrency=max_concurrency)
    assert repr(scheduler) == f'RateLimiter({mock_bucket!r}, should_enter_context=False, {max_concurrency=})'
