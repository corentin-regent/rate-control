import os.path
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Any, Optional

import pytest


class SubTests:
    @contextmanager
    def test(self, msg: Optional[str] = None, **kwargs: Any) -> Iterator[None]:
        yield  # pragma: no cover


@pytest.mark.slow
def test_examples(subtests: SubTests) -> None:
    for python_file, output_file in _python_and_output_files():
        with subtests.test(msg=python_file.name):
            module_name = str(python_file.with_suffix('')).replace(os.path.sep, '.')
            with open(output_file) as f:
                expected = f.read()
            with StringIO() as buffer, redirect_stdout(buffer):
                import_module(module_name)
                actual = buffer.getvalue()
            assert actual == expected


def _python_and_output_files() -> Iterator[tuple[Path, Path]]:
    for output_file in Path('docs/examples').glob('**/*.out'):
        for lib in ('asyncio', 'trio', 'anyio'):
            python_file = Path(f'{output_file.with_suffix("")}_{lib}.py')
            yield python_file, output_file
