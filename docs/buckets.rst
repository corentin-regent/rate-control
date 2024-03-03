Bucket algorithms
=================

.. _`fixed-window-counter`:

:class:`.FixedWindowCounter`
----------------------------

The fixed window counter is the simplest algorithm,
which is why it is used by most API gateways out there.

The timeline is divided into windows of ``duration`` seconds,
during each of which can be consumed only ``capacity`` tokens.

Each window starts when a request is first received,
which means a new window does not necessarily
start right after the previous one. 

When it is time for a new window, all tokens of the bucket are replenished,
which may lead to request bursts, as well as a violation of the rate limit:
more than ``capacity`` tokens can be consumed within ``duration`` seconds,
if considering a cross-window period of time.

:class:`.LeakyBucket`
---------------------

The leaky bucket accepts only 1 request every ``delay`` seconds.

It is a good choice when you want to maintain a constant throughput of requests.

:class:`.SlidingWindowLog`
--------------------------

The most accurate rate limiting is provided by the sliding window log algorithm.

The bucket has a given token ``capacity`` and window ``duration``.
Incoming requests consume a certain amount of tokens from the bucket,
and the tokens consumed by each request are replenished
``duration`` seconds after the request has been made.

:class:`.UnlimitedBucket`
-------------------------

As the name suggests, the :class:`.UnlimitedBucket` has no restriction on
the amount of tokens it can acquire.

It can be useful for situations where you would like to set
a concurrency limit but no rate limits per se, for example
if you are looking to prevent overwhelming your web server with requests.

Integrating custom bucket algorithms
------------------------------------

If the available algorithms do not fit your needs, please consider
:doc:`contributing </contributing>` to Rate Control,
or just create it in your own project if it is too specific.

All you have to do is implement the :class:`.Bucket` abstract class,
and you will be ready to go!
