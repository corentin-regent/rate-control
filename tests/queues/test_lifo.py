from collections.abc import Iterable, Sequence
from itertools import chain

import pytest

from rate_control._errors import Empty
from rate_control.queues import LifoQueue


@pytest.fixture
def queue(any_elements: Iterable[object]) -> LifoQueue[object]:
    return LifoQueue(*any_elements)


def test_nominal(queue: LifoQueue[object], any_elements: Sequence[object]) -> None:
    other_elems = ('first', b'second')
    for other_elem in other_elems:
        queue.add(other_elem)

    for elem in chain(reversed(other_elems), reversed(any_elements)):
        assert queue
        assert queue.head() == elem
        assert queue.pop() == elem

    assert not queue
    with pytest.raises(Empty):
        queue.head()
    with pytest.raises(Empty):
        queue.pop()


def test_removing_any_elements(queue: LifoQueue[object], any_elements: Sequence[object]) -> None:
    last_elem = any_elements[-1]
    assert queue.head() == last_elem

    queue.remove(last_elem)
    assert queue.head() != last_elem
    while queue:
        assert queue.pop() != last_elem

    with pytest.raises(ValueError):
        queue.remove(last_elem)


def test_repr() -> None:
    queue = LifoQueue(2, 1, 3)
    queue.add(4)
    assert repr(queue) == 'LifoQueue(4, 3, 1, 2)'
