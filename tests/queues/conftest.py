import sys

import pytest

if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence


@pytest.fixture
def any_elements() -> Sequence[object]:
    return (123.456, 'test', -42, b'anything', None)
