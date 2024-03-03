import pytest


@pytest.fixture
def max_concurrency(some_positive_int: int) -> int:
    return some_positive_int


@pytest.fixture
def max_pending(some_positive_int: int) -> int:
    return some_positive_int
