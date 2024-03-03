import pytest


@pytest.fixture
def some_valid_capacity(capacity: float) -> float:
    return capacity


@pytest.fixture
def int_capacity(capacity: float) -> int:
    return int(capacity)


@pytest.fixture
def some_valid_delay(delay: float) -> float:
    return delay


@pytest.fixture
def some_valid_duration(duration: float) -> float:
    return duration


@pytest.fixture
def tiny_delay() -> float:
    return 1e-4
