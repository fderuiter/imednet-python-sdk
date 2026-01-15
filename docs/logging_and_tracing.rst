Logging and Tracing
===================

The :class:`imednet.core.client.Client` uses standard Python logging. It does not
configure logging handlers or formatters by default, respecting the consuming
application's configuration.

You can opt-in to JSON formatted logging by calling
:func:`imednet.utils.json_logging.configure_json_logging` in your application.

If `opentelemetry` is installed, the client can record spans around each HTTP
request. Installing ``opentelemetry-instrumentation-httpx`` will automatically
instrument the HTTPX requests used by the SDK. You may also pass your own
tracer to the client.

Example configuration::

   from opentelemetry import trace
   from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
   from imednet.core.client import Client

   HTTPXClientInstrumentor().instrument()
   tracer = trace.get_tracer(__name__)
   client = Client(api_key="A", security_key="B", tracer=tracer)

Request Lifecycle
-----------------

The client logs each request and, when a tracer is supplied, surrounds the HTTP call
with a span.

.. mermaid::

   sequenceDiagram
       participant App
       participant Client
       participant HTTPX
       App->>Client: call endpoint
       Client->>Client: start span (optional)
       Client->>HTTPX: send request
       HTTPX-->>Client: response
       Client->>Client: log JSON
       Client->>Client: end span (optional)
       Client-->>App: return result
