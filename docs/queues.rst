Request queues
==============

The :class:`.Scheduler` queues requests using the queue algorithm
you pass to its constructor. This page is a reference for these algorithms.

:class:`.PriorityQueue`
-----------------------

The priority queue sorts requests so that they are processed by ascending weight.

This allows to let through more lightweight requests,
that could otherwise be blocked by a heavier one.

.. note::
    Requests with identical weights are not guaranteed
    to be processed in the order they arrived.

:class:`.FifoQueue`
-------------------

The "First In, First Out" queue schedules requests so that
they are processed in the order they arrive.

:class:`.LifoQueue`
-------------------

The "Last In, First Out" queue schedules requests so that
the latest ones are processed first.
