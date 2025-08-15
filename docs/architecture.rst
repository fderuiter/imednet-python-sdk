Architecture Overview
=====================

The SDK is organized around a core HTTP client layer, endpoint wrappers that model
the iMednet API, workflow helpers that combine multiple endpoint calls, and a CLI
built on top of those pieces.

Components
----------

.. mermaid::

   graph TD
       CLI[CLI] --> |invokes| Workflows
       Workflows --> |coordinate| Endpoints
       Endpoints --> |use| Client[HTTP Client]
       Client --> |requests| API

Core Client
-----------

The synchronous :class:`~imednet.core.client.Client` implements authentication,
retry handling, and JSON serialization for each API request. It inherits from
``HTTPClientBase`` and is shared by all endpoint classes.

Async Client
------------

:class:`~imednet.core.async_client.AsyncClient` provides the same features as the
sync client but leverages ``async``/``await`` for concurrency. The
:class:`~imednet.sdk.ImednetSDK` exposes both clients via ``sdk.client`` and
``sdk.async_client``.

Endpoints
---------

Each endpoint, such as :class:`~imednet.endpoints.studies.StudiesEndpoint`,
wraps a related set of API operations. Endpoints can cache responses when called
without filters and expose ``list``/``get`` methods that return typed models.

Workflows
---------

Workflows orchestrate several endpoints to perform higher level tasks. For
example, :class:`~imednet.workflows.record_update.RecordUpdateWorkflow` validates
record payloads, submits them, and polls resulting jobs. Workflows have sync and
async variants and are available under ``sdk.workflows``.

Caching
-------

:doc:`caching` describes how endpoint and schema data are cached. Cached values
can be refreshed by passing ``refresh=True`` to endpoint methods or calling
``schema.refresh()`` on a validator.

CLI
---

The :doc:`cli` uses `Typer` to expose common workflows on the command line. Each
command creates an :class:`~imednet.sdk.ImednetSDK` instance, invokes a workflow,
and closes the SDK when finished.

Data Flow
---------

.. mermaid::

   graph LR
       User --> |runs| CLI
       User --> |imports| SDK
       CLI --> |uses| Workflows
       SDK --> |exposes| Endpoints
       Workflows --> |call| Endpoints
       Endpoints --> |delegate| Client
       Client --> |talks to| API
       Client --> |uses| Cache[Caches]

Extension Points
----------------

.. mermaid::

   graph TD
       BaseEndpoint --> NewEndpoint[Custom Endpoint]
       Workflows --> NewWorkflow[Custom Workflow]
       NewEndpoint --> |register| SDK
       NewWorkflow --> |expose via| CLI

Adding New Endpoints
--------------------

* Subclass :class:`~imednet.endpoints.base.BaseEndpoint`.
* Register the class in ``_ENDPOINT_REGISTRY`` within
  :mod:`imednet.sdk` so ``ImednetSDK`` exposes it.
* Document the endpoint in ``docs/endpoints/`` and add tests.

Adding New Workflows
--------------------

* Create a workflow under ``imednet/workflows`` and provide sync and async
  methods where appropriate.
* Instantiate the workflow in ``Workflows`` inside :mod:`imednet.sdk`.
* Add CLI commands or examples that demonstrate the workflow.
* Update documentation and tests.

