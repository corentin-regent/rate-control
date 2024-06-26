import pytest

from rate_control._helpers._request import Request
from rate_control.queues import FifoQueue, LifoQueue, PriorityQueue


@pytest.mark.parametrize(
    'obj',
    [
        FifoQueue(),
        LifoQueue(),
        PriorityQueue(),
        Request(1),
    ],
)
def test_slots(obj: object) -> None:
    assert not hasattr(obj, '__dict__')
