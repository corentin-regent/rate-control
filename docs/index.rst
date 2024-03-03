============
Rate Control
============

*Versatile rate controlling in Python*

Key Features
------------

* Rate limiting
* Scheduling requests
* Request synchronization
* Request prioritization
* Chaining buckets
* Support for both asyncio_ and Trio_, through AnyIO_
* Support for task cancellation

.. _AnyIO: https://github.com/agronholm/anyio
.. _asyncio: https://docs.python.org/3/library/asyncio.html
.. _Trio: https://github.com/python-trio/trio

Contributing
------------

Contributions are very welcome. Please read :doc:`Contributing </contributing>` for details.


.. toctree::
   :caption: Documentation
   :hidden:

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
