Weighting requests
==================

Sometimes, some requests are more resource-intensive than others.
You may want to allow making more less of these heavy requests
than for lightweight ones.

Here is how you can specify a cost for each request with Rate Control:

.. tabs::
    .. group-tab:: Asyncio
        .. literalinclude:: examples/asyncio/weighting_requests.py
    .. group-tab:: Trio
        .. literalinclude:: examples/trio/weighting_requests.py
    .. group-tab:: AnyIO
        .. literalinclude:: examples/anyio/weighting_requests.py

.. literalinclude:: examples/weighting_requests.out
    :language: text
    :caption: Output
