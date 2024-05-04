__all__ = [
    'Queue',
]

import sys
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

_T = TypeVar('_T')


class Queue(ABC, Generic[_T]):
    """Abstract class for representing a queue."""

    __slots__ = ()

    @abstractmethod
    def __bool__(self) -> bool:
        """Returns whether the queue contains at least one element"""

    @abstractmethod
    @override
    def __repr__(self) -> str:
        """String representation of the queue.

        The elements appear in the order they will be popped.
        """

    @abstractmethod
    def head(self) -> _T:
        """
        Returns:
            The element at the head of the queue.

        Raises:
            Empty: The queue is empty.
        """

    @abstractmethod
    def pop(self) -> _T:
        """Remove the element at the head of the queue, and return it.

        Returns:
            The element at the head of the queue.

        Raises:
            Empty: The queue is empty.
        """

    @abstractmethod
    def add(self, element: _T) -> None:
        """Add the given element to the queue.

        Args:
            element: The element in question.
        """

    @abstractmethod
    def remove(self, element: _T) -> None:
        """Delete the given element from the queue.

        Args:
            element: The element in question.

        Raises:
            ValueError: The element is not present in the queue.
        """
