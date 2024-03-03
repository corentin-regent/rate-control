__all__ = [
    'Duration',
]

from enum import IntEnum


class Duration(IntEnum):
    """Common durations that may be used to define bucket refill delays."""

    SECOND = 1
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
