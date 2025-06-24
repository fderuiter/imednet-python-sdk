Intervals Endpoint
==================

The ``intervals`` resource lists the scheduled intervals (or visits) for a
study. Each interval defines a set of forms that must be completed for a
subject. A visit is a single instance of an interval for a given subject.

Accessing the index
-------------------

Use ``GET`` to retrieve intervals for a study. The request supports paging,
sorting and filtering.

Example request::

   GET /api/v1/edc/studies/PHARMADEMO/intervals?page=0&size=25&sort=intervalId%2CASC&filter=intervalId%3D%3D161 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
~~~~~~~~~~~~~~~

``studyKey``
  Study key used to retrieve intervals.

Request parameters
~~~~~~~~~~~~~~~~~~

``page``
  Index page to return. Defaults to ``0``.

``size``
  Items per page. Defaults to ``25``. Maximum ``500``.

``sort``
  Property used to sort the result set. Add ``asc`` or ``desc`` after the
  property name to specify direction. Multiple ``sort`` parameters are allowed.
  Default ``intervalId,asc``.

``filter``
  Optional filter criteria. See :doc:`../rest_api_reference` for syntax.

Response body
-------------

Example payload::

   {
     "metadata" : {
       "status" : "OK",
       "method" : "GET",
       "path" : "/api/v1/edc/studies/PHARMADEMO/intervals",
       "timestamp" : "2025-06-05 21:12:08",
       "error" : { }
     },
     "pagination" : {
       "currentPage" : 0,
       "size" : 25,
       "totalPages" : 1,
       "totalElements" : 1,
       "sort" : [ {
         "property" : "intervalId",
         "direction" : "ASC"
       } ]
     },
     "data" : [ {
       "studyKey" : "PHARMADEMO",
       "intervalId" : 1,
       "intervalName" : "Day 1",
       "intervalDescription" : "Day 1",
       "intervalSequence" : 110,
       "intervalGroupId" : 10,
       "intervalGroupName" : "ePRO",
       "disabled" : true,
       "dateCreated" : "2025-06-05 21:12:08",
       "dateModified" : "2025-06-05 21:12:09",
       "timeline" : "Start Date End Date",
       "definedUsingInterval" : "Baseline",
       "windowCalculationForm" : "Procedure",
       "windowCalculationDate" : "PROCDT",
       "actualDateForm" : "Follow Up",
       "actualDate" : "FUDT",
       "dueDateWillBeIn" : 30,
       "negativeSlack" : 7,
       "positiveSlack" : 7,
       "eproGracePeriod" : 2,
       "forms" : [ {
         "formId" : 123,
         "formKey" : "MY-FORM-KEY",
         "formName" : "myFormName"
       } ]
     } ]
   }

Response fields
---------------

``metadata.status``
  HTTP status.

``metadata.method``
  HTTP method.

``metadata.path``
  Request URI path.

``metadata.timestamp``
  Timestamp when the response was generated.

``metadata.error``
  Error details when a request fails.

``pagination.currentPage``
  Current index page.

``pagination.size``
  Page size.

``pagination.totalPages``
  Total pages returned.

``pagination.totalElements``
  Total elements returned.

``pagination.sort[].property``
  Sort property.

``pagination.sort[].direction``
  Sort direction.

``data[].studyKey``
  Study key.

``data[].intervalId``
  Unique interval identifier.

``data[].intervalName``
  Interval or visit name.

``data[].intervalDescription``
  Interval description.

``data[].intervalSequence``
  Sequence number.

``data[].intervalGroupId``
  Interval group ID.

``data[].intervalGroupName``
  Interval group name.

``data[].timeline``
  Type of interval visit window.

``data[].definedUsingInterval``
  Baseline interval where the calculate-from date is collected.

``data[].windowCalculationForm``
  Baseline form where the calculate-from date is collected.

``data[].windowCalculationDate``
  Baseline field used to calculate dates.

``data[].actualDateForm``
  Actual date form for the interval.

``data[].actualDate``
  Actual date field for the interval.

``data[].dueDateWillBeIn``
  Number of days the actual date is due from the calculate-from date.

``data[].negativeSlack``
  Allowed negative days from the due date.

``data[].positiveSlack``
  Allowed positive days from the due date.

``data[].eproGracePeriod``
  Allowed positive days for ePRO from the due date.

``data[].forms[].formId``
  Form ID.

``data[].forms[].formKey``
  Form key.

``data[].forms[].formName``
  Form name.

``data[].disabled``
  Interval soft-delete status.

``data[].dateCreated``
  Date when the interval was created.

``data[].dateModified``
  Date when the interval was last modified.

`Portal docs <https://portal.prod.imednetapi.com/docs/intervals>`_

