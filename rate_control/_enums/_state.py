__all__ = [
    'State',
]

from enum import Enum, auto


class State(Enum):
    """The current state of the context manager."""

    UNENTERED = auto()
    """The object has been instantiated, but its context has not been entered."""

    ENTERED = auto()
    """The context manager is currently in use, within a ``with`` block."""

    CLOSED = auto()
    """The context manager has been exited, the ``with`` block has ended."""
