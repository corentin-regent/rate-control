Scheduling requests
===================

Overview
--------

Anticipating rate limit errors for your client is great,
but wouldn't it be neat if you could play along with these constraints,
and schedule rate limited requests to be executed when
the restrictions are loose again?

This is the purpose of Rate Control's :class:`.Scheduler`.
If the underlying bucket allows for the request to be executed,
then it is fired instantly. Otherwise, the request is placed in a queue,
and will be executed as soon as possible.

Usage
^^^^^

Here is how the :class:`.Scheduler` can be used:

.. tabs::
    .. group-tab:: Asyncio
        .. literalinclude:: examples/asyncio/scheduler.py
    .. group-tab:: Trio
        .. literalinclude:: examples/trio/scheduler.py
    .. group-tab:: AnyIO
        .. literalinclude:: examples/anyio/scheduler.py

.. literalinclude:: examples/scheduler.out
    :language: text
    :caption: Output

Similarly, the :class:`.Scheduler` can postpone jobs
if the specified ``max_concurrency`` was reached,
to be processed when another request exits the
:meth:`~rate_control.Scheduler.schedule` context.

Fill or kill
^^^^^^^^^^^^

You can choose to fall back to the simple rate limiting behavior
for a given request, by providing a ``fill_or_kill=True`` argument
to :meth:`~rate_control.Scheduler.schedule`.

The :exc:`.RateLimit` exception will be raised if the request
cannot be processed instantly.

.. _prioritization:

Request prioritization
----------------------

Queuing requests
^^^^^^^^^^^^^^^^

By default, scheduled jobs are placed in a queue,
and will be executed by ascending cost,
and in the order they were received if these weights are equal.

A complete reference of the queue algorithms offered by
Rate Control can be found on :doc:`this page </queues>`.

Specifying a :enum:`.Priority`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes, some functionalities of your application may be more critical than others.

In order to schedule the execution of important requests before the others,
:meth:`~rate_control.Scheduler.schedule` can take a ``priority`` argument.

Under the hood, there is one request queue for each available priority level.
Therefore, requests with higher priority will bypass the queue
algorithms that apply within a same priority level.
