Mednet EDC REST API Reference
=============================

This page summarizes the core behavior of the iMednet REST API. It expands upon
:doc:`api_overview` and serves as a quick reference for request structure and
filter syntax.

Overview
--------

The API exposes clinical study data via JSON responses. Consumers typically use
the API to export data to reporting tools, present it in external
applications, or compile custom audit trails.

Base URL
--------

``https://edc.prod.imednetapi.com`` is the production endpoint. Append an
endpoint route such as ``/api/v1/edc/studies`` to access resources.

Security
--------

Each request requires ``x-api-key`` and ``x-imn-security-key`` headers. Keys
should never be shared publicly. Example using ``curl``::

   curl -X GET https://edc.prod.imednetapi.com/api/v1/edc/studies/STUDYKEY/sites \
     -H 'x-api-key: XXXXXXXX' \
     -H 'x-imn-security-key: XXX-XXX-XX-XXXXXX' \
     -H 'Content-Type: application/json'

HTTP verbs
----------

``GET`` retrieves resources while ``POST`` is used to insert data.

Status codes
------------

``200``
  Request succeeded.

``400``
  Malformed request.

``401``
  Authentication failed.

``403``
  Authorization error such as an invalid ``studyKey``.

``404``
  Resource not found.

``429``
  Too many requests.

``500``
  Unknown server error.

Filtering
---------

Endpoints accept a ``filter`` query string composed of key, operator and value
segments. ``recordDataFilter`` targets dynamic question data within a record.

Attributes
~~~~~~~~~~

Valid attributes vary per endpoint. Common examples include ``studyKey`` for
studies, ``siteId`` and ``siteName`` for sites, ``formId`` and ``formKey`` for
forms, and ``dateCreated`` or ``dateModified`` for most resources.

Operators
~~~~~~~~~

``<``  less than

``<=`` less than or equal to

``>``  greater than

``>=`` greater than or equal to

``==`` equal

``!=`` not equal

``=~`` contains (for ``recordDataFilter``)

Connectors
~~~~~~~~~~

``and`` or ``;``  logical AND

``or``  or `,`     logical OR

Dates
~~~~~

Dates are UTC timestamps. When filtering visits by ``startDate``,
``endDate``, ``dueDate`` or ``visitDate`` use the ``YYYY-MM-DD`` format.

Filter examples
~~~~~~~~~~~~~~~

``formId > 10``
  Forms with an ID greater than 10.

``formType == "SUBJECT"``
  Subject related forms.

``formId > 10;formType == "SUBJECT"``
  Subject related forms with ID greater than 10.

``dateCreated>2000-11-05T14:00:00Z``
  Entities created after 5 November 2000 14:00 UTC.

``visitDate<2019-03-19``
  Visits occurring before 19 March 2019.

recordDataFilter examples
~~~~~~~~~~~~~~~~~~~~~~~~~

``AESER==Serious``
  Serious adverse events.

``AESER==Serious;GENDER==Male``
  Serious adverse events for male subjects.

``AESER==bronch``
  Adverse events containing ``bronch``.

Notes
~~~~~

White space is not allowed between attribute, operator and value. Both ``filter``
and ``recordDataFilter`` require unique attributes and are case sensitive.
