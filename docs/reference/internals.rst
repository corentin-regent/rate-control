Internals
=========

This section documents private internal objects *for reference*.
You will not need to manipulate them directly unless
you are seeking to contribute to the library.

Controller mixins
-----------------

.. autoclass:: rate_control._controllers._bucket_based.BucketBasedRateController

Bucket mixins
-------------

.. autoclass:: rate_control._buckets._base.TokenBasedBucket
   :no-inherited-members:

.. autoclass:: rate_control._buckets._base.BaseRateBucket

.. autoclass:: rate_control._buckets._base.BaseWindowedTokenBucket

.. autoclass:: rate_control._buckets._base.CapacityUpdatingBucket
    :no-inherited-members:

Miscellaneous
-------------

.. autoclass:: rate_control._helpers.Request

.. autoclass:: rate_control._helpers._protocols.Comparable

.. autoclass:: rate_control._helpers.ContextAware

Enumerations
------------

.. autoenum:: rate_control._enums.State
    :no-inherited-members:

Exceptions
----------

.. autoexception:: rate_control._errors.Empty
   :no-inherited-members:
