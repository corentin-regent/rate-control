__all__ = [
    'Comparable',
]

import sys
from abc import abstractmethod
from typing import Protocol

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class Comparable(Protocol):
    __slots__ = ()

    @abstractmethod
    def __lt__(self, other: Self, /) -> bool:
        """Comparison operator.

        Args:
            other: Another object of the same type.

        Returns:
            Whether ``self < other``.
        """
