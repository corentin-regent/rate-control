import pytest

from rate_control import (
    BucketGroup,
    FixedWindowCounter,
    LeakyBucket,
    NoopController,
    RateLimiter,
    Scheduler,
    SlidingWindowLog,
)
from rate_control._helpers._request import Request
from rate_control.queues import FifoQueue, LifoQueue, PriorityQueue


@pytest.mark.parametrize(
    'obj',
    [
        BucketGroup(),
        FixedWindowCounter(1, 1),
        LeakyBucket(1),
        NoopController(),
        RateLimiter(),
        Scheduler(),
        SlidingWindowLog(1, 1),
        FifoQueue(),
        LifoQueue(),
        PriorityQueue(),
        Request(1),
    ],
)
def test_slots(obj: object) -> None:
    assert not hasattr(obj, '__dict__')
