import os.path
import sys
from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

if sys.version_info >= (3, 9):
    from builtins import tuple as Tuple
    from collections.abc import Iterator
else:
    from typing import Iterator, Tuple


@pytest.mark.slow
def test_examples(subtests: Any) -> None:
    for python_file, output_file in _python_and_output_files():
        module_name = str(python_file.with_suffix('')).replace(os.path.sep, '.')
        with open(output_file) as f:
            expected = f.read()
        with StringIO() as buffer, redirect_stdout(buffer):
            import_module(module_name)
            actual = buffer.getvalue()
        with subtests.test(msg=python_file.name):
            assert actual == expected


def _python_and_output_files() -> Iterator[Tuple[Path, Path]]:
    root_path = Path('docs/examples')
    for output_file in root_path.glob('*.out'):
        for lib in ('asyncio', 'trio', 'anyio'):
            python_file = root_path / lib / output_file.name.replace('.out', '.py')
            yield python_file, output_file
