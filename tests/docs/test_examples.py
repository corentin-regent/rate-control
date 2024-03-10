import os.path
from contextlib import redirect_stdout
from importlib import import_module
from io import StringIO
from pathlib import Path
from typing import Any

import pytest


@pytest.mark.slow
def test_examples(subtests: Any) -> None:
    examples_path = Path('docs/examples')
    for python_file in examples_path.glob('*.py'):
        expected_output_file = python_file.with_suffix('.out')
        module_name = str(python_file.with_suffix('')).replace(os.path.sep, '.')
        with open(expected_output_file) as f:
            expected = f.read()
        with StringIO() as buffer, redirect_stdout(buffer):
            import_module(module_name)
            actual = buffer.getvalue()
        with subtests.test(msg=python_file.name):
            assert actual == expected
