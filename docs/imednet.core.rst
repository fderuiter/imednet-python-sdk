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

