Changelog
=========

This library adheres to `Semantic Versioning 2.0 <http://semver.org/>`_.

Unreleased
----------

API changes
^^^^^^^^^^^

* **Breaking change**: Unified the API for the rate controllers.

  * Now both the ``RateLimiter`` and the ``Scheduler`` use the following signature:
    ``async with controller.request(tokens): ...``

  * The ``RateLimiter`` can now also be instantiated in an ``async with RateLimiter(...)`` statement.

Miscellaneous
^^^^^^^^^^^^^

* The ``RateController`` base class, and all buckets,
  are now exported in the main ``rate_control`` module.

1.1.0
-----

Added the ability to update the token capacity for ``FixedWindowCounter`` and ``SlidingWindowLog``.

1.0.0
-----

First release of the project
