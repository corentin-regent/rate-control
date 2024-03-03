__all__ = [
    'mk_repr',
]

from itertools import chain, starmap
from typing import Any


def mk_repr(obj: object, *args: Any, **kwargs: Any) -> str:
    """Build the string representation of the given object.

    Args:
        obj: The object to make a string representation for.
        args: The positional arguments passed to ``obj``'s constructor.
        kwargs: The keyword arguments passed to ``obj``'s constructor.

    Returns:
        The object's string representation.
    """
    args_repr = map(repr, args)
    kwargs_repr = starmap(_mk_key_value_repr, kwargs.items())
    params_repr = ', '.join(chain(args_repr, kwargs_repr))
    return f'{type(obj).__name__}({params_repr})'


def _mk_key_value_repr(key: str, value: Any) -> str:
    return f'{key}={value!r}'
