Request synchronization
=======================

Sometimes, you may want to define a maximum amount
of requests running concurrently.

For this purpose, a ``max_concurrency`` parameter
can be specified to the rate controller:

.. tabs::
    .. group-tab:: Asyncio
        .. literalinclude:: examples/max_concurrency/max_concurrency_asyncio.py
    .. group-tab:: Trio
        .. literalinclude:: examples/max_concurrency/max_concurrency_trio.py
    .. group-tab:: AnyIO
        .. literalinclude:: examples/max_concurrency/max_concurrency_anyio.py

.. literalinclude:: examples/max_concurrency/max_concurrency.out
    :language: text
    :caption: Output
