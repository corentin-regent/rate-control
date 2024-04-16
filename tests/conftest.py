import secrets
import sys
from asyncio import get_running_loop
from unittest.mock import AsyncMock, Mock

import pytest
from aiofastforward import FastForward
from anyio import create_task_group
from anyio.abc import TaskGroup
from pytest import Function, Parser

from rate_control import Bucket, FixedWindowCounter

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Sequence
else:
    from typing import AsyncIterator, Sequence


def pytest_addoption(parser: Parser) -> None:
    parser.addoption('--runslow', action='store_true', help='Run slow tests')


def pytest_runtest_setup(item: Function) -> None:
    if 'slow' in item.keywords and not item.config.getoption('--runslow'):
        pytest.skip('Need --runslow option to run this test')


@pytest.fixture(scope='module')
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture
async def fast_forward() -> AsyncIterator[FastForward]:
    loop = get_running_loop()
    with FastForward(loop) as forward:
        yield forward


@pytest.fixture
async def task_group() -> AsyncIterator[TaskGroup]:
    async with create_task_group() as _task_group:
        yield _task_group
        _task_group.cancel_scope.cancel()


def _mk_mock_bucket() -> Mock:
    mock = Mock(Bucket)
    mock.acquire = Mock()
    mock.__aenter__ = AsyncMock()
    mock.__aexit__ = AsyncMock()
    return mock


@pytest.fixture
def mock_buckets() -> Sequence[Mock]:
    return [_mk_mock_bucket() for _ in range(10)]


@pytest.fixture
def mock_bucket(mock_buckets: Sequence[Mock]) -> Mock:
    return secrets.choice(mock_buckets)


@pytest.fixture
async def fixed_window_counter(capacity: float, duration: float) -> AsyncIterator[FixedWindowCounter]:
    async with FixedWindowCounter(capacity, duration) as bucket:
        yield bucket


@pytest.fixture
def capacity() -> float:
    return 12.21


@pytest.fixture
def delay() -> float:
    return 12.34


@pytest.fixture
def duration(delay: float) -> float:
    return delay


@pytest.fixture
def aeons() -> float:
    return 123456.789


@pytest.fixture
def any_token(capacity: float) -> float:
    return capacity / 123.456


@pytest.fixture
def some_tokens() -> float:
    return 12


@pytest.fixture
def some_negative_value() -> float:
    return -12.3456


@pytest.fixture
def some_negative_int(some_negative_value: float) -> int:
    return int(some_negative_value)


@pytest.fixture
def some_positive_int(some_negative_int: int) -> int:
    return -some_negative_int
