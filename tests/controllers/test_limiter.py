from contextlib import ExitStack
from functools import partial
from unittest.mock import Mock

import pytest

from rate_control import Bucket, RateLimit, RateLimiter
from tests import assert_not_raises


@pytest.fixture
def rate_limiter(mock_bucket: Mock, max_concurrency: int) -> RateLimiter:
    return RateLimiter(mock_bucket, max_concurrency=max_concurrency)


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
        rate_limiter.hold(some_tokens + any_token).__enter__()
    mock_bucket.acquire.assert_not_called()

    with rate_limiter.hold(some_tokens):
        mock_bucket.acquire.assert_called_once_with(some_tokens)


@pytest.mark.anyio
async def test_max_concurrency(rate_limiter: RateLimiter, mock_bucket: Mock, max_concurrency: int) -> None:
    mock_bucket.can_acquire = Mock(return_value=True)
    with ExitStack() as stack:
        for _ in range(max_concurrency - 1):
            assert rate_limiter.can_acquire()
            stack.enter_context(rate_limiter.hold())

        with rate_limiter.hold():
            assert not rate_limiter.can_acquire()
            with pytest.raises(RateLimit):
                rate_limiter.hold().__enter__()

        assert rate_limiter.can_acquire()
        with assert_not_raises():
            with rate_limiter.hold():
                pass


@pytest.mark.anyio
async def test_repr(mock_bucket: Bucket, max_concurrency: int) -> None:
    scheduler = RateLimiter(mock_bucket, max_concurrency=max_concurrency)
    assert repr(scheduler) == f'RateLimiter(bucket={mock_bucket!r}, {max_concurrency=})'
