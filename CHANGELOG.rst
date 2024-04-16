Changelog
=========

This library adheres to `Semantic Versioning 2.0 <http://semver.org/>`_.

Unreleased
----------

Nothing changed yet.

2.0.0
-----

Breaking changes
^^^^^^^^^^^^^^^^

* Unified the API for the rate controllers.

  * Now both the ``RateLimiter`` and the ``Scheduler`` use the following signature:
    ``async with controller.request(tokens): ...``

  * The ``RateLimiter`` can now also be instantiated in an ``async with RateLimiter(...)`` statement.

* Rate controllers now manage their bucket's context in their ``async with`` statement,
  so that we don't need to enter manually the bucket's context and then the rate controller's context.
  This behavior can be disabled using the ``should_enter_context`` flag in the constructor.

* The ``rate_control.buckets`` module is now private.
  The ``RateController`` base class, and all buckets,
  are now exported in the main ``rate_control`` module.

New Features
^^^^^^^^^^^^

* The ``BucketGroup`` class now implements the ``Iterable[Bucket]`` protocol.

1.1.0
-----

Added the ability to update the token capacity for ``FixedWindowCounter`` and ``SlidingWindowLog``.

1.0.0
-----

First release of the project
