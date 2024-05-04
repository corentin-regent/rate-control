__all__ = [
    'Request',
]

import sys
from typing import Any

from anyio import Event

from rate_control._helpers._protocols import Comparable

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class Request(Comparable):
    """Represents a user's request for tokens"""

    __slots__ = ('_ack_event', 'cost', '_validation_event')

    def __init__(self, cost: float, **kwargs: Any) -> None:
        """
        Args:
            cost: The number of tokens requested.
        """
        super().__init__(**kwargs)
        self.cost = cost
        self._validation_event = Event()
        self._ack_event = Event()

    @override
    def __lt__(self, other: Self) -> bool:
        """Comparison operator so that requests can be placed
        in a priority queue and processed by ascending cost.
        """
        return self.cost < other.cost

    async def wait_for_validation(self) -> None:
        """Wait until the request has been fired."""
        await self._validation_event.wait()

    def fire(self) -> None:
        """Fire the request."""
        self._validation_event.set()

    async def wait_for_ack(self) -> None:
        """Wait until the request has been acknowledged."""
        await self._ack_event.wait()

    def ack(self) -> None:
        """Acknowledge the request."""
        self._ack_event.set()
