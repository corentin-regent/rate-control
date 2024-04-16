Weighting requests
==================

Sometimes, some requests are more resource-intensive than others.
You may want to allow making less of these heavy requests
and more lightweight ones.

Here is how you can specify a cost for each request with Rate Control:

.. tabs::
    .. group-tab:: Asyncio
        .. literalinclude:: examples/weighting_requests/weighting_requests_asyncio.py
    .. group-tab:: Trio
        .. literalinclude:: examples/weighting_requests/weighting_requests_trio.py
    .. group-tab:: AnyIO
        .. literalinclude:: examples/weighting_requests/weighting_requests_anyio.py

.. literalinclude:: examples/weighting_requests/weighting_requests.out
    :language: text
    :caption: Output
