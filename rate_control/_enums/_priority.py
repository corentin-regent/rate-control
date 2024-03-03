__all__ = [
    'Priority',
]

from enum import IntEnum


class Priority(IntEnum):
    """The priority of a request.

    Requests with higher priority will be processed before the others by schedulers.
    """

    HIGHEST = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    LOWEST = 4


assert [p.value for p in Priority] == list(range(len(Priority)))
