Quickstart
==========

Installation
------------

Rate Control requires Python 3.8 or later to run.

The library is hosted on `PyPI <https://pypi.org/project/rate-control/>`_,
you can install it using pip:

.. code-block:: bash

    pip install rate-control

.. _rate-limiting:

Basic usage
-----------

Suppose you want to design a client-side rate controller for accessing
some external API, to prevent your application from receiving responses with code
`429 <https://developer.mozilla.org/docs/Web/HTTP/Status/429>`_.

Rate Control can help you track your requests,
and handle rate limit errors before they occur.

.. warning::
    Due to network fluctuations and other external factors, it is *not guaranteed*
    that the usage of these rate controllers will free you from all rate limit-related
    errors when requesting an API. You should still have a plan to handle such errors,
    though they will be much more rare.

Below is a simple example of how you could use a rate limiter,
to ensure that no more than two requests are handled each minute.

.. note::
    All available bucket algorithms are explained
    on the :doc:`dedicated page </buckets>`.

.. literalinclude:: examples/rate_limiter.py
.. literalinclude:: examples/rate_limiter.out.txt
    :language: text
    :caption: Output

Rate Control has much more functionalities to offer.
Keep browsing this documentation to discover all the
flexibility that this library can provide.
