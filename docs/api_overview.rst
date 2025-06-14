API Overview
===========

This page summarizes the core concepts of the Mednet EDC REST API and how the
SDK interacts with it.

Base URL
--------

The SDK communicates with the production API at
``https://edc.prod.imednetapi.com`` by default. Override this with the
``IMEDNET_BASE_URL`` environment variable if using a private deployment.

Authentication
--------------

All requests must include ``x-api-key`` and ``x-imn-security-key`` headers. The
:class:`~imednet.core.client.Client` and :class:`~imednet.core.async_client.AsyncClient`
read ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` from the environment and
populate these headers automatically.

HTTP methods and errors
-----------------------

The API primarily supports ``GET`` and ``POST`` requests. Non‐successful status
codes raise typed exceptions:

* ``400`` – :class:`~imednet.core.exceptions.ValidationError`
* ``401`` – :class:`~imednet.core.exceptions.AuthenticationError`
* ``403`` – :class:`~imednet.core.exceptions.AuthorizationError`
* ``404`` – :class:`~imednet.core.exceptions.NotFoundError`
* ``429`` – :class:`~imednet.core.exceptions.RateLimitError`
* ``5xx`` – :class:`~imednet.core.exceptions.ServerError`

Filtering
---------

Endpoints accept a ``filter`` parameter that matches the syntax documented in the
Mednet API guide. For clinical data queries, ``recordDataFilter`` can be supplied
alongside ``filter``. See :mod:`imednet.endpoints.records` for usage examples.

Some endpoints (:class:`~imednet.endpoints.studies.StudiesEndpoint`,
:class:`~imednet.endpoints.forms.FormsEndpoint`,
:class:`~imednet.endpoints.intervals.IntervalsEndpoint`, and
:class:`~imednet.endpoints.variables.VariablesEndpoint`) maintain an internal
cache. They accept a ``refresh`` argument to force a reload of cached data. This
flag is not a general filtering option and has no effect on other endpoints.

Dates must use UTC timestamps except where noted. When filtering visits by
``startDate``, ``dueDate``, ``endDate`` or ``visitDate``, use ``YYYY-MM-DD``.
String values containing spaces or special characters must be wrapped in
double quotes. For example: ``siteName=="My Site"``.

