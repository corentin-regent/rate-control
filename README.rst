============
Rate Control
============

*Versatile rate controlling in Python*

======= =========================================================
CI/CD   |release| |ci| |docs|
Package |python-version| |package-version| |license|
Quality |coverage| |quality-gate| |maintainability| |reliability|
Meta    |type-check| |code-style|
======= =========================================================

Documentation
=============

Full documention can be found at https://rate-control.readthedocs.io/

Key Features
============

* `Rate limiting <https://rate-control.readthedocs.io/en/latest/quickstart.html#basic-usage>`_
* `Scheduling requests <https://rate-control.readthedocs.io/en/latest/scheduling.html>`_
* `Request synchronization <https://rate-control.readthedocs.io/en/latest/synchronization.html>`_
* `Request prioritization <https://rate-control.readthedocs.io/en/latest/scheduling.html#request-prioritization>`_
* `Chaining buckets <https://rate-control.readthedocs.io/en/latest/bucket-groups.html>`_
* Supports task cancellation
* Supports both asyncio_ and Trio_, through AnyIO_

.. _AnyIO: https://github.com/agronholm/anyio
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _Trio: https://github.com/python-trio/trio

Contributing
============

Contributions are very welcome. Please read `CONTRIBUTING </CONTRIBUTING.rst>`_ for details.


.. CI/CD:

.. |release| image:: https://github.com/corentin-regent/rate-control/actions/workflows/release.yml/badge.svg
  :alt: Release
  :target: https://github.com/corentin-regent/rate-control/actions/workflows/release.yml

.. |ci| image:: https://github.com/corentin-regent/rate-control/actions/workflows/ci.yml/badge.svg
  :alt: Continuous Integration
  :target: https://github.com/corentin-regent/rate-control/actions/workflows/ci.yml

.. |docs| image:: https://readthedocs.org/projects/rate-control/badge/?version=latest
  :alt: Documentation Status
  :target: https://rate-control.readthedocs.io/

.. Package:

.. |python-version| image:: https://img.shields.io/pypi/pyversions/rate-control?logo=python
  :alt: Python Versions

.. |package-version| image:: https://img.shields.io/pypi/v/rate-control?logo=python
  :alt: Package Version
  :target: https://pypi.org/project/rate-control/

.. |license| image:: https://img.shields.io/pypi/l/rate-control?logo=unlicense
  :alt: MIT License
  :target: https://rate-control.readthedocs.io/en/latest/license.html

.. Quality:

.. |coverage| image:: https://img.shields.io/sonar/coverage/corentin-regent_rate-control?server=https%3A%2F%2Fsonarcloud.io&logo=sonarcloud
  :alt: Code Coverage
  :target: https://sonarcloud.io/summary/new_code?id=corentin-regent_rate-control

.. |quality-gate| image:: https://sonarcloud.io/api/project_badges/measure?project=corentin-regent_rate-control&metric=alert_status
  :alt: Quality Gate
  :target: https://sonarcloud.io/summary/new_code?id=corentin-regent_rate-control

.. |maintainability| image:: https://sonarcloud.io/api/project_badges/measure?project=corentin-regent_rate-control&metric=sqale_rating
  :alt: Maintainability Rating
  :target: https://sonarcloud.io/summary/new_code?id=corentin-regent_rate-control

.. |reliability| image:: https://sonarcloud.io/api/project_badges/measure?project=corentin-regent_rate-control&metric=reliability_rating
  :alt: Reliability Rating
  :target: https://sonarcloud.io/summary/new_code?id=corentin-regent_rate-control

.. Meta:

.. |type-check| image:: https://www.mypy-lang.org/static/mypy_badge.svg
  :alt: Type Checked
  :target: https://mypy-lang.org/

.. |code-style| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
  :alt: Code Style
  :target: https://github.com/astral-sh/ruff
