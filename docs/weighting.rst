Weighting requests
==================

Sometimes, some requests are more resource-intensive than others.
You may want to allow making more less of these heavy requests
than for lightweight ones.

Here is how you can specify a cost for each request with Rate Control:

.. literalinclude:: examples/weighting_requests.py
.. literalinclude:: examples/weighting_requests.out.txt
    :language: text
    :caption: Output
