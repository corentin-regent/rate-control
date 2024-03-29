Internals
=========

This section documents private internal objects *for reference*.
You will not need to manipulate them directly unless
you are seeking to contribute to the library.

Base classes
------------

Controllers
^^^^^^^^^^^

.. autoclass:: rate_control._controllers._base.RateController

Buckets
^^^^^^^

.. autoclass:: rate_control.buckets._base.TokenBasedBucket
   :no-inherited-members:

.. autoclass:: rate_control.buckets._base.BaseRateBucket

.. autoclass:: rate_control.buckets._base.BaseWindowedTokenBucket

Miscellaneous
-------------

.. autoclass:: rate_control._helpers.Request

.. autoclass:: rate_control._helpers._protocols.Comparable

Exceptions
----------

.. autoexception:: rate_control._errors.Empty
   :no-inherited-members:
