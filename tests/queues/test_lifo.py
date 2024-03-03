import sys
from itertools import chain
from typing import Any

import pytest

from rate_control._errors import Empty
from rate_control.queues import LifoQueue

if sys.version_info >= (3, 9):
    from collections.abc import Iterable, Sequence
else:
    from typing import Iterable, Sequence


@pytest.fixture
def elements() -> Sequence[Any]:
    return (123.456, 'test', -42, Any)


@pytest.fixture
def queue(elements: Iterable[Any]) -> LifoQueue[Any]:
    return LifoQueue(*elements)


def test_nominal(queue: LifoQueue[Any], elements: Sequence[Any]) -> None:
    latest_elems = ['first', 'second']
    for elem in latest_elems:
        queue.add(elem)

    for elem in chain(reversed(latest_elems), reversed(elements)):
        assert queue
        assert queue.head() == elem
        assert queue.pop() == elem

    assert not queue
    with pytest.raises(Empty):
        queue.head()
    with pytest.raises(Empty):
        queue.pop()


def test_removing_elements(queue: LifoQueue[Any], elements: Sequence[Any]) -> None:
    last_elem = elements[-1]
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
