Retry Policy and Error Handling
===============================

``RetryPolicy`` decouples retry decisions from the underlying tenacity logic.
The default implementation only retries for network errors raised by ``httpx``.
You can implement your own strategy by inspecting :class:`imednet.core.retry.RetryState`.

Handling exceptions
-------------------

Use typed exceptions to respond to different failure modes:

.. code-block:: python

   from imednet import ImednetSDK
   from imednet.core.exceptions import RateLimitError, ServerError, NotFoundError

   sdk = ImednetSDK()
   try:
       sdk.studies.list()
   except RateLimitError:
       print("Too many requests, try again later")
   except NotFoundError as exc:
       print(f"Missing resource: {exc}")
   except ServerError as exc:
       print(f"Server error: {exc}")

Custom strategies
-----------------

Retry policies decide if a request should be retried. To retry on
``RateLimitError`` and ``ServerError``:

.. code-block:: python

   from imednet.core.client import Client
   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.core.exceptions import RateLimitError, ServerError

   class RateLimitServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, (RateLimitError, ServerError))

   client = Client(
       api_key="A",
       security_key="B",
       retries=5,
       backoff_factor=0.5,
       retry_policy=RateLimitServerRetry(),
   )

Logging and exponential backoff
-------------------------------

Each attempt is logged with JSON formatting. Configure logging globally via
:func:`imednet.utils.configure_json_logging` or by supplying ``log_level`` when
constructing the client. Retries use exponential backoff with delays controlled
by ``retries`` and ``backoff_factor``. With ``retries=5`` and ``backoff_factor=0.5``
the wait times are 0.5 s, 1 s, 2 s, 4 s, and 8 s.

Example script
--------------

The :doc:`examples/custom_retry` script demonstrates these concepts using a mock
transport:

.. code-block:: console

   export IMEDNET_API_KEY=dummy
   export IMEDNET_SECURITY_KEY=dummy
   python examples/custom_retry.py
