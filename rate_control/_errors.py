__all__ = [
    'Empty',
    'RateLimit',
    'ReachedMaxPending',
]


class Empty(Exception):
    """Collection is empty."""


class RateLimit(Exception):
    """Cannot process the incoming request."""


class ReachedMaxPending(Exception):
    """Reached the maximum allowed pending requests."""
