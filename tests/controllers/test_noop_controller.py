import sys
from unittest.mock import Mock

import pytest
from anyio import create_task_group

from rate_control import Bucket, NoopController
from tests import assert_not_raises

if sys.version_info >= (3, 9):
    from collections.abc import AsyncIterator, Collection, Iterable
else:
    from typing import AsyncIterator, Collection, Iterable


@pytest.fixture
async def noop_controller() -> AsyncIterator[NoopController]:
    async with NoopController() as controller:
        yield controller


def test_init(mock_buckets: Iterable[Bucket]) -> None:
    with assert_not_raises():
        NoopController()
    with assert_not_raises():
        NoopController(*mock_buckets)


@pytest.mark.anyio
async def test_can_acquire(noop_controller: NoopController, some_positive_int: int) -> None:
    for _ in range(some_positive_int):
        assert noop_controller.can_acquire()
        with assert_not_raises():
            async with noop_controller.request():
                ...

    with assert_not_raises():
        async with create_task_group() as task_group:
            for _ in range(some_positive_int):
                task_group.start_soon(noop_controller.request().__aenter__)


@pytest.mark.anyio
async def test_not_enter_buckets_context(mock_buckets: Collection[Mock]) -> None:
    async with NoopController(*mock_buckets):
        for bucket in mock_buckets:
            bucket.__aenter__.assert_not_called()
    for bucket in mock_buckets:
        bucket.__aexit__.assert_not_called()


@pytest.mark.anyio
async def test_singleton(mock_buckets: Iterable[Bucket]) -> None:
    assert NoopController() is NoopController(*mock_buckets)


@pytest.mark.anyio
async def test_chaotic_context_management(noop_controller: NoopController) -> None:
    # Such situation can happen in the real world, as the same singleton
    # object is used everywhere in the client code
    request_cm = noop_controller.request()
    async with noop_controller.request(), noop_controller:
        async with noop_controller:
            async with noop_controller.request():
                await noop_controller.__aexit__()
                await request_cm.__aenter__()
        async with noop_controller.request():
            await noop_controller.__aenter__()
            await request_cm.__aexit__(None, None, None)


@pytest.mark.anyio
async def test_repr(mock_bucket: Bucket) -> None:
    controller = NoopController(mock_bucket)
    assert repr(controller) == 'NoopController()'
