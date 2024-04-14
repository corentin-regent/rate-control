Using bucket groups
===================

Chaining multiple buckets
-------------------------

Sometimes you may want to enforce several rate limit constraints for your application.
For example, many API gateways define both a long-running rate limitation,
as well as a one that watches a shorter period of time.

For example, if you want to interact with the Github API,
`here <https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api>`_
are **some** specifications for the rate limits:

* 5000 requests are allowed per hour.
* 900 *points* are allowed per minute per REST API endpoint.

Below is how you could implement such rate limiting strategy using Rate Control.
Shorter periods of time are used so that you can run this example at home:

* 2 requests are allowed every second.
* 3 requests are allowed over each 2-second window.

.. tabs::
    .. group-tab:: Asyncio
        .. literalinclude:: examples/bucket_group/bucket_group_asyncio.py
    .. group-tab:: Trio
        .. literalinclude:: examples/bucket_group/bucket_group_trio.py
    .. group-tab:: AnyIO
        .. literalinclude:: examples/bucket_group/bucket_group_anyio.py

.. literalinclude:: examples/bucket_group/bucket_group.out
    :language: text
    :caption: Output

Composite buckets
-----------------

:class:`.BucketGroup` is a subclass of :class:`.Bucket`.
Therefore, everything you may do with buckets, you can also do with bucket groups,
may it be consuming tokens, waiting for refill, or even forming token groups of token groups!
