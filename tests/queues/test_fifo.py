import sys
from itertools import chain

import pytest

from rate_control._errors import Empty
from rate_control.queues import FifoQueue

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Sequence
else:
    from typing import Iterable, Sequence


@pytest.fixture
def queue(any_elements: Iterable[object]) -> FifoQueue[object]:
    return FifoQueue(*any_elements)


def test_nominal(queue: FifoQueue[object], any_elements: Sequence[object]) -> None:
    other_elems = ('first', b'second')
    for elem in other_elems:
        queue.add(elem)

    for elem in chain(any_elements, other_elems):
        assert queue
        assert queue.head() == elem
        assert queue.pop() == elem

    assert not queue
    with pytest.raises(Empty):
        queue.head()
    with pytest.raises(Empty):
        queue.pop()


def test_removing_any_elements(queue: FifoQueue[object], any_elements: Sequence[object]) -> None:
    first_elem = any_elements[0]
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
