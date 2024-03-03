__all__ = [
    'Queue',
    'FifoQueue',
    'LifoQueue',
    'PriorityQueue',
]

from ._abc import Queue
from ._fifo import FifoQueue
from ._lifo import LifoQueue
from ._priority import PriorityQueue
