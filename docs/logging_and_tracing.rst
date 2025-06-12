Logging and Tracing
===================

The :class:`imednet.core.client.Client` configures JSON formatted logging when it
is instantiated. You can adjust the log level with the ``log_level`` parameter or
call :func:`imednet.utils.configure_json_logging` in your application to apply the
same format globally.

If `opentelemetry` is installed, the client can record spans around each HTTP
request. Installing ``opentelemetry-instrumentation-requests`` will automatically
instrument the underlying HTTPX calls. You may also pass your own tracer to the
client.

Example configuration::

   from opentelemetry import trace
   from opentelemetry.instrumentation.requests import RequestsInstrumentor
   from imednet.core.client import Client

   RequestsInstrumentor().instrument()
   tracer = trace.get_tracer(__name__)
   client = Client(api_key="A", security_key="B", tracer=tracer)
