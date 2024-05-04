import math
import sys
from itertools import chain

import pytest

from rate_control._errors import Empty
from rate_control._helpers._protocols import Comparable
from rate_control.queues import PriorityQueue

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Sequence
else:
    from typing import Iterable, Sequence


@pytest.fixture
def elements() -> Sequence[float]:
    return (123.456, 0, -42, math.inf)


@pytest.fixture
def queue(elements: Iterable[float]) -> PriorityQueue[float]:
    return PriorityQueue(*elements)


def test_nominal(queue: PriorityQueue[float], elements: Sequence[float]) -> None:
    other_elems = (1.5, 999)
    for elem in other_elems:
        queue.add(elem)

    for elem in sorted(chain(elements, other_elems)):
        assert queue
        assert queue.head() == elem
        assert queue.pop() == elem

    assert not queue
    with pytest.raises(Empty):
        queue.head()
    with pytest.raises(Empty):
        queue.pop()


def test_removing_elements(queue: PriorityQueue[Comparable], elements: Sequence[float]) -> None:
    lowest_valued_elem = min(elements)
    assert queue.head() == lowest_valued_elem

    queue.remove(lowest_valued_elem)
    assert queue.head() != lowest_valued_elem
    while queue:
        assert queue.pop() != lowest_valued_elem

    with pytest.raises(ValueError):
        queue.remove(lowest_valued_elem)


def test_repr() -> None:
    queue = PriorityQueue(2, 1, 3)
    queue.add(4)
    assert repr(queue) == 'PriorityQueue(1, 2, 3, 4)'
