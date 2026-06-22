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

Contract Drift Telemetry
------------------------

The SDK proactively monitors API responses for schema drift against its internal models.
When an undocumented field is received or a field changes type, the SDK logs a warning
via the ``imednet.drift`` logger.

These logs allow developers to identify breaking API changes or additive field additions
before they cause systemic regressions. 

**Additive Drift:** New undocumented fields are logged as additive drift. The SDK drops
these fields during model creation but warns the user.
**Destructive Drift:** Missing required fields or changed field types (e.g. from integer
to dictionary) are logged as destructive drift. In many cases these will raise
validation errors, but the drift logger isolates the root cause.

To monitor for drift, ensure your application captures warnings from the ``imednet.drift``
logger.

Request Lifecycle
-----------------

The client logs each request and, when a tracer is supplied, surrounds the HTTP call
with a span.

.. mermaid:: diagrams/logging_and_tracing_1.mmd