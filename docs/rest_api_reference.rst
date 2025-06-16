Mednet EDC REST API Reference
=============================

.. contents::
   :local:
   :depth: 2

Overview
--------

The Mednet EDC REST API exposes read and write access to clinical trial data. Clients
issue HTTP requests against a centralized service. Responses are returned as JSON.

Base URL
--------

All endpoints are rooted under ``https://edc.prod.imednetapi.com``. To request a
resource, append the route to this base URL. For example::

   https://edc.prod.imednetapi.com/api/v1/edc/studies

Headers
-------

All endpoints require the following request headers:

* ``Accept`` - must be ``application/json``
* ``x-api-key`` - your iMednet supplied API key
* ``x-imn-security-key`` - your iMednet supplied security key
* ``Content-Type`` - must be ``application/json``

Responses always include ``Content-Type: application/json``.

Keep your credentials secret. The SDK reads the API and security keys from the
environment and sets these headers automatically.


HTTP Verbs and Status Codes
---------------------------

``GET`` retrieves resources and ``POST`` inserts data. Typical status codes are:

- ``200`` – success
- ``400`` – malformed request
- ``401`` – unauthorized
- ``403`` – forbidden
- ``404`` – not found
- ``429`` – too many requests
- ``500`` – server error

Filtering
---------

Results can be filtered using the ``filter`` query parameter. Attributes are
case sensitive and vary by endpoint. A few examples::

   formId > 10
   formType == "SUBJECT"
   formId > 10;formType == "SUBJECT"

Use ``and`` or ``;`` to combine conditions and ``or`` or ``,`` for alternatives.
Dates are expressed in UTC using ``YYYY-MM-DDTHH:MM:SSZ`` unless searching
``startDate``, ``dueDate``, ``endDate`` or ``visitDate``, which use ``YYYY-MM-DD``.

Record Data Filters
-------------------

``recordDataFilter`` lets you query inside ``recordData``. Only ``;`` or ``,`` can
be used at a time. Example::

   AESER==Serious;GENDER==Male

Preconditions
-------------

- Criteria are separated by ``;`` or ``,`` with no whitespace.
- Values follow the operator immediately.
- Searches are case sensitive.
- ``dateCreated`` and ``dateModified`` require full UTC timestamps.


Error responses
---------------

When a request fails, error details are returned in the ``metadata`` section of the response body. Validation errors include the offending field and value. Example::

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

For additional details see the `common API reference <https://portal.prod.imednetapi.com/docs/common>`_.
