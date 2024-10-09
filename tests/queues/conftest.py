from collections.abc import Sequence

import pytest


@pytest.fixture
def any_elements() -> Sequence[object]:
    return (123.456, 'test', -42, b'anything', None)
