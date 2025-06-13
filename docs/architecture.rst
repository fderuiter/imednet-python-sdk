Architecture Overview
=====================

The SDK is organized around a core HTTP client, endpoint wrappers, higher level workflows,
and a command line interface. The diagram below illustrates how these pieces interact.

.. mermaid::

   graph TD
       CLI[CLI] --> |uses| Workflows
       CLI --> |calls| SDK
       Workflows --> |call| SDK
       SDK --> |wraps| Endpoints
       Endpoints --> |use| HTTPClient

