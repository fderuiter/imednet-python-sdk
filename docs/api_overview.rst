API Overview
============

This page summarizes the core concepts of the Mednet EDC REST API and how the
SDK interacts with it.

Base URL
--------

The SDK communicates with the production API at
``https://edc.prod.imednetapi.com`` by default. Override this with
``IMEDNET_BASE_URL`` or the ``base_url`` argument to ``load_config`` for a
private deployment. See :doc:`configuration` for details.

Authentication
--------------

All requests must include ``x-api-key`` and ``x-imn-security-key`` headers. The
:class:`~imednet.core.base_client.BaseClient` handles shared initialization
while the :class:`~imednet.core.client.Client` and
:class:`~imednet.core.async_client.AsyncClient` rely on
:func:`imednet.config.load_config` to read ``IMEDNET_API_KEY`` and
``IMEDNET_SECURITY_KEY`` from the environment and populate these headers
automatically. See :doc:`configuration` for more information.

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

See :doc:`retry_policy` for examples of handling these errors and configuring
custom retry logic.

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

Filter helper
-------------

Use :func:`imednet.utils.filters.build_filter_string` to construct filter
expressions from a mapping. Values containing spaces must be wrapped in double
quotes. Example::

   build_filter_string({"site_name": "Bright Test Site"})
   # siteName=="Bright Test Site"

Error responses
---------------

When a request fails, error details are returned in the ``metadata`` section of
the response body. Validation errors include the offending field and value.
Example::

   {
     "metadata": {
       "status": "BAD_REQUEST",
       "path": "/api/v1/edc/studies",
       "timestamp": "2018-10-18 05:46:29",
       "error": {
         "code": "1000",
         "description": "Field raised validation errors",
         "field": {
           "attribute": "page",
           "value": "XX"
         }
       }
     }
   }

Error response fields
~~~~~~~~~~~~~~~~~~~~~

``code``
  Error code

``description``
  Error description message

``field.attribute``
  Origination request attribute which caused the error

``field.value``
  The value of request attribute passed in the request

Error codes
~~~~~~~~~~~

``1000``
  Validation error. Request contain invalid value.

``9000``
  Unknown error. Please contact Mednet support for assistance.

``9001``
  Unauthorized error. Insufficient permission to retrieve data.

