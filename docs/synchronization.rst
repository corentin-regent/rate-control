Request synchronization
=======================

Sometimes, you may want to define a maximum amount
of requests running concurrently.

For this purpose, a ``max_concurrency`` parameter
can be specified to the rate controller:

.. literalinclude:: examples/max_concurrency.py
.. literalinclude:: examples/max_concurrency.out
    :language: text
    :caption: Output
