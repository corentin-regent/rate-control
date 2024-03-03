import sys
from itertools import chain
from typing import Any

import pytest

from rate_control._errors import Empty
from rate_control.queues import FifoQueue

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Sequence
else:
    from typing import Iterable, Sequence


@pytest.fixture
def elements() -> Sequence[Any]:
    return (123.456, 'test', -42, Any)


@pytest.fixture
def queue(elements: Iterable[Any]) -> FifoQueue[Any]:
    return FifoQueue(*elements)


def test_nominal(queue: FifoQueue[Any], elements: Sequence[Any]) -> None:
    other_elems = ['first', 'second']
    for elem in other_elems:
        queue.add(elem)

    for elem in chain(elements, other_elems):
        assert queue
        assert queue.head() == elem
        assert queue.pop() == elem

    assert not queue
    with pytest.raises(Empty):
        queue.head()
    with pytest.raises(Empty):
        queue.pop()


def test_removing_elements(queue: FifoQueue[Any], elements: Sequence[Any]) -> None:
    first_elem = elements[0]
    assert queue.head() == first_elem

    queue.remove(first_elem)
    assert queue.head() != first_elem
    while queue:
        assert queue.pop() != first_elem

    with pytest.raises(ValueError):
        queue.remove(first_elem)


def test_repr() -> None:
    queue = FifoQueue(2, 1, 3)
    queue.add(4)
    assert repr(queue) == 'FifoQueue(2, 1, 3, 4)'
