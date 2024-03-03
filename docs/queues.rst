Request queues
==============

Available queues
----------------

:class:`.PriorityQueue`
^^^^^^^^^^^^^^^^^^^^^^^

The priority queue sorts requests so that they are processed by ascending weight.

This allows to let through more lightweight requests,
that could otherwise be blocked by a heavier one.

.. warning::
    Requests with identical weight are not guaranteed
    to be processed in the order they arrived.

:class:`.FifoQueue`
^^^^^^^^^^^^^^^^^^^

The "First In, First Out" queue schedules requests so that
they are processed in the order they arrive.

:class:`.LifoQueue`
^^^^^^^^^^^^^^^^^^^

The "Last In, First Out" queue schedules requests so that
the latest ones are processed first.

Integrating a custom queue algorithm
------------------------------------

None of these options fit your needs? We've got you covered!

All you have to do is create your own
implementation of the :class:`.Queue` abstract class,
pass it as an argument of the :class:`.Scheduler`,
and you will be ready to go!

