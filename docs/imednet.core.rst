imednet.core package
====================

The :class:`~imednet.core.client.Client` emits JSON formatted logs and can record OpenTelemetry
 spans when a tracer is provided. See :doc:`logging_and_tracing` for details.

Submodules
----------

imednet.core.client module
--------------------------

.. automodule:: imednet.core.client
   :members:
   :undoc-members:
   :show-inheritance:

imednet.core.base_client module
-------------------------------

.. automodule:: imednet.core.base_client
   :members:
   :undoc-members:
   :show-inheritance:

imednet.core.context module
---------------------------


Logging and tracing
-------------------
The :class:`imednet.core.client.Client` can emit JSON formatted logs of each HTTP
request when you configure logging:

.. code-block:: python

    from imednet.utils import configure_json_logging
    from imednet.core.client import Client

    configure_json_logging()
    client = Client(api_key="...", security_key="...", log_level="INFO")

If ``opentelemetry`` is installed, pass a tracer instance or rely on the global
tracer provider. Each request is executed within a span and works with
``opentelemetry-instrumentation-httpx`` for automatic context propagation of the
HTTPX requests used by the SDK:

.. code-block:: python

    from opentelemetry import trace
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    HTTPXClientInstrumentor().instrument()
    tracer = trace.get_tracer("my-app")
    client = Client(api_key="...", security_key="...", tracer=tracer)
.. automodule:: imednet.core.context
   :members:
   :undoc-members:
   :show-inheritance:

imednet.core.exceptions module
------------------------------

.. automodule:: imednet.core.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

imednet.core.paginator module
-----------------------------

.. automodule:: imednet.core.paginator
   :members:
   :undoc-members:
   :show-inheritance:

Retry policy
------------

The :class:`~imednet.core.retry.RetryPolicy` interface controls if failed
requests should be retried. The SDK uses
``DefaultRetryPolicy`` which retries when ``httpx`` raises a
``RequestError``. Provide your own policy to customize this behaviour.

.. code-block:: python

   from imednet.core.client import Client
   from imednet.core.retry import RetryPolicy, RetryState
   from imednet.core.exceptions import ServerError

   class ServerRetry(RetryPolicy):
       def should_retry(self, state: RetryState) -> bool:
           return isinstance(state.exception, ServerError)

   client = Client("A", "B", retry_policy=ServerRetry())

