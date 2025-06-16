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

Security and Validation
-----------------------

Every request requires two headers::

   x-api-key: your-imednet-supplied-api-key
   x-imn-security-key: your-imednet-supplied-security-key

Keep these credentials secret. The SDK reads them from environment variables and
adds the headers automatically.

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

