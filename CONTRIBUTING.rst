Contributing
============

Prerequisites
-------------

Please follow `this guide <https://python-poetry.org/docs/>`_
to install poetry if you don't have it already.

All the commands that you may use are grouped in the root Makefile.
So please make sure that you have `Make <https://www.gnu.org/software/make/>`_
in your environment, otherwise you can just copy the commands from the Makefile
and paste them in your terminal.

Setting up
----------

In order to install the project, required dependencies, and to configure
`pre-commit <https://pre-commit.com/>`_ hooks, you can run ``make install``.

Testing
-------

Running tests
^^^^^^^^^^^^^

Tests can be run with pytest using ``make test``.

Some tests are marked as *slow*. By default they are not executed.
you can run them using ``make test-runslow``.

Test coverage
^^^^^^^^^^^^^

You can check your test coverage locally by using the
`coverage <https://coverage.readthedocs.io/>`_ package
through ``make coverage``.

All the tests will be run, including the slow ones.

An HTML report will be generated in the ``htmlcov`` directory
at the root of the project, highlighting which lines
of code were not covered by the tests.

Linting and code formatting
---------------------------

`Ruff <https://docs.astral.sh/ruff/>`_ is used for linting and formatting our code.
It can be run using the ``make lint`` and ``make format`` commands.

These two actions will also be run every time you commit changes,
by the pre-commit hook. The commit will fail after the files are changed by ruff,
so that you can take a look and stage these changes before validating.

Type checking
-------------

This project ensures strict type checking using `mypy <https://github.com/python/mypy>`_.
In order to check whether your changes are correctly typed,
you can run ``make type-check``.

Documentation
-------------

All user-exposed classes, methods and functions you add must be documented, following the
`Google style guide <https://google.github.io/styleguide/pyguide.html>`_.

The documentation is built using `Sphinx <https://sphinx-doc.org>`_.
You can generate it locally using ``make docs``.

Also, do not forget to update the CHANGELOG and describe your changes!
