__all__ = [
    'PriorityQueue',
]

import sys
from heapq import heapify, heappop, heappush
from typing import Any, TypeVar

from rate_control._errors import Empty
from rate_control._helpers import mk_repr
from rate_control._helpers._protocols import Comparable
from rate_control.queues._abc import Queue

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


_T = TypeVar('_T', bound=Comparable)


class PriorityQueue(Queue[_T]):
    """Queue where the lowest valued elements are retrieved first.

    Warning:
        Equally valued elements are not guaranteed to be retrieved
        in the order they arrived.
    """

    __slots__ = ('_queue',)

    def __init__(self, *elements: _T, **kwargs: Any) -> None:
        """
        Args:
            elements: The elements to initialize the queue with.
        """
        self._queue = list(elements)
        heapify(self._queue)
        super().__init__(**kwargs)

    @override
    def __repr__(self) -> str:
        return mk_repr(self, *sorted(self._queue))

    @override
    def __bool__(self) -> bool:
        return bool(self._queue)

    @override
    def head(self) -> _T:
        try:
            return self._queue[0]
        except IndexError as e:
            raise Empty from e

    @override
    def pop(self) -> _T:
        try:
            return heappop(self._queue)
        except IndexError as e:
            raise Empty from e

    @override
    def add(self, element: _T) -> None:
        return heappush(self._queue, element)

    @override
    def remove(self, element: _T) -> None:
        self._queue.remove(element)
        heapify(self._queue)
