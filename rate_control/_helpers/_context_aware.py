__all__ = [
    'ContextAware',
]

import sys
from abc import ABC
from contextlib import AbstractAsyncContextManager
from typing import Any, Optional

from rate_control._enums import State

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override


class ContextAware(AbstractAsyncContextManager[Any], ABC):
    """Mixin for raising an exception if the async context manager is entered more than once."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = State.UNENTERED

    @override
    async def __aenter__(self) -> Any:
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
        self._state = State.CLOSED
        return await super().__aexit__(*exc_info)
