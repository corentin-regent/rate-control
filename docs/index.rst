============
Rate Control
============

*Versatile rate controlling in Python*

Key Features
------------

* :ref:`Rate limiting <rate-limiting>`
* :doc:`Scheduling requests </scheduling>`
* :doc:`Request synchronization </synchronization>`
* :ref:`Request prioritization <prioritization>`
* :doc:`Chaining buckets </bucket-groups>`
* Supports task cancellation
* Supports both asyncio_ and Trio_, through AnyIO_

.. _AnyIO: https://github.com/agronholm/anyio
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _Trio: https://github.com/python-trio/trio

Documentation index
-------------------

.. toctree::
   :caption: Documentation
   :maxdepth: 2

   quickstart
   weighting
   synchronization
   scheduling
   bucket-groups
   buckets
   queues
   reference/index


.. toctree::
   :caption: Project information
   :hidden:

   license
   changelog
   contributing
