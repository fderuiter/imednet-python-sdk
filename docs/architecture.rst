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
       Endpoints --> |use| Client["(HTTP Client)"]
       Client --> |httpx| API

Core Client
-----------

The synchronous :class:`~imednet.core.client.Client` implements authentication,
retry handling, and JSON serialization for each API request. It inherits from
``HTTPClientBase`` and is shared by all endpoint classes. HTTP transport is
handled by ``httpx``.

HTTP Transport Contract
-----------------------

The transport layer in :mod:`imednet.core.http` provides the following guarantees:

Retry policy
~~~~~~~~~~~~

* Retries are evaluated by :class:`imednet.core.retry.DefaultRetryPolicy`.
* Idempotent methods (``GET``, ``PUT``, ``DELETE``, ``HEAD``, ``OPTIONS``) retry on:

  * ``httpx.RequestError`` network failures
  * HTTP ``5xx`` responses
* All methods (including ``POST``/``PATCH``) retry on HTTP ``429`` rate limits.
* Non-idempotent methods do not retry on network errors or ``5xx`` responses.
* Maximum attempts are controlled by the ``retries`` argument on
  :class:`~imednet.core.client.Client`,
  :class:`~imednet.core.async_client.AsyncClient`,
  :class:`~imednet.sdk.ImednetSDK`, and :class:`~imednet.sdk.AsyncImednetSDK`.
* Backoff uses Tenacity's randomized exponential wait strategy with
  ``backoff_factor`` as the multiplier.
* If a retriable response includes ``Retry-After``, that delay overrides the
  backoff schedule.

Timeouts
~~~~~~~~

* ``timeout`` is forwarded directly into ``httpx.Client`` / ``httpx.AsyncClient``.
* You can pass either a float (single timeout applied to all phases) or
  ``httpx.Timeout`` for per-phase timeouts.

Status-code error mapping
~~~~~~~~~~~~~~~~~~~~~~~~~

Response errors are mapped via :func:`imednet.errors.get_error_class`:

.. list-table::
   :header-rows: 1

   * - Status code
     - Raised exception
   * - 400
     - :class:`imednet.errors.BadRequestError`
   * - 401
     - :class:`imednet.errors.UnauthorizedError`
   * - 403
     - :class:`imednet.errors.ForbiddenError`
   * - 404
     - :class:`imednet.errors.NotFoundError`
   * - 409
     - :class:`imednet.errors.ConflictError`
   * - 429
     - :class:`imednet.errors.RateLimitError`
   * - 500-599
     - :class:`imednet.errors.ServerError`
   * - other
     - :class:`imednet.errors.ApiError`

Credential redaction
~~~~~~~~~~~~~~~~~~~~

* Transport logs never include raw credential headers.
* URLs logged by request monitoring are sanitized through
  :func:`imednet.utils.url.redact_url_query`, redacting sensitive query params
  such as ``api_key``, ``security_key``, ``token``, ``secret``, and ``password``.
* Retry exhaustion raises :class:`imednet.errors.RequestError` with a generic
  message that does not expose credentials.

Async Client
------------

:class:`~imednet.core.async_client.AsyncClient` provides the same features as the
sync client but leverages ``async``/``await`` for concurrency. The public SDK
surface is split into two client classes:

* :class:`~imednet.sdk.ImednetSDK` for synchronous usage only.
* :class:`~imednet.sdk.AsyncImednetSDK` for asynchronous usage only.

Migration note: if you previously used async behavior from ``ImednetSDK``, move
to :class:`~imednet.sdk.AsyncImednetSDK` and manage lifecycle with
``async with`` or ``await sdk.aclose()``.

Endpoints
---------

Each endpoint, such as :class:`~imednet.endpoints.studies.StudiesEndpoint`,
wraps a related set of API operations. Endpoints now use **composition**:
`GenericListGetEndpoint` composes operation classes (for example
``ListOperation`` and ``FilterGetOperation``) rather than inheriting deep
operation mixin chains. This keeps method resolution straightforward, improves
IDE autocomplete, and avoids MRO-related typing ambiguity. Endpoints can cache
responses when called without filters and expose ``list``/``get`` methods that
return typed models.

Workflows
---------

Workflows orchestrate several endpoints to perform higher level tasks. For
example, :class:`~imednet_workflows.record_update.RecordUpdateWorkflow` validates
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
       Client --> |uses| Cache["(Caches)"]

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

* Subclass :class:`~imednet.core.endpoint.base.GenericEndpoint` or
  :class:`~imednet.core.endpoint.base.GenericListGetEndpoint`.
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
