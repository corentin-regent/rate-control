__all__ = [
    'ContextAware',
]

import sys
from abc import ABC
from typing import Any, Optional

from rate_control._enums import State

if sys.version_info >= (3, 9):
    from contextlib import AbstractAsyncContextManager as _AbstractAsyncContextManager

    class AbstractAsyncContextManager(_AbstractAsyncContextManager[Any]): ...
else:
    from contextlib import AbstractAsyncContextManager


if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class ContextAware(AbstractAsyncContextManager, ABC):
    """Mixin for raising an exception if the async context manager is entered more than once."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = State.UNENTERED

    @override
    async def __aenter__(self) -> Any:
        """Sets the state of the context manager to :py:enum:mem:`State.ENTERED`.

        Raises:
            RuntimeError: The context manager has already been entered.
        """
        if self._state is not State.UNENTERED:
            raise RuntimeError(
                'Cannot enter the context manager more than once.'
                if self._state is State.ENTERED
                else 'Cannot reopen the context manager once it has been closed.'
            )
        self._state = State.ENTERED
        return await super().__aenter__()

    @override
    async def __aexit__(self, *exc_info: Any) -> Optional[bool]:
        """Sets the state of the context manager to :py:enum:mem:`State.CLOSED`."""
        self._state = State.CLOSED
        return await super().__aexit__(*exc_info)
