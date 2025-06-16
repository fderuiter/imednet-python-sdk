Record Revisions Endpoint
=========================

Given a ``StudyKey``, fetch the set of record revisions. Each revision represents a distinct state
in the lifecycle of a record. Every time data is modified on a record or it progresses to a new
status, a new record revision is captured.

Accessing the index
-------------------

A ``GET`` request is used to access the index.

.. code-block:: http

   GET /api/v1/edc/studies/PHARMADEMO/recordRevisions?page=0&size=25&sort=recordRevisionId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path Parameters
---------------

``studyKey``
    Study key to retrieve list of record revisions.

Request Parameters
------------------

``page``
    Index page to return. Default is ``0``.
``size``
    Items per page. Default is ``25``. Maximum is ``500``.
``sort``
    Sort property. Append ``asc`` or ``desc`` for direction. Default is ``recordRevisionId,asc``.
``filter``
    Optional filter criteria. See :ref:`filter` for syntax details.

Response
--------

Example response payload:

.. code-block:: json

   {
     "metadata": {
       "status": "OK",
       "method": "GET",
       "path": "/api/v1/edc/studies/PHARMADEMO/recordRevisions",
       "timestamp": "2025-06-05 21:12:09",
       "error": {}
     },
     "pagination": {
       "currentPage": 0,
       "size": 25,
       "totalPages": 1,
       "totalElements": 1,
       "sort": [
         {
           "property": "recordRevisionId",
           "direction": "ASC"
         }
       ]
     },
     "data": [
       {
         "studyKey": "PHARMADEMO",
         "recordRevisionId": 1,
         "recordId": 1,
         "recordOid": "REC-1",
         "recordRevision": 1,
         "dataRevision": 1,
         "recordStatus": "Record Complete",
         "subjectId": 247,
         "subjectOid": "OID-1",
         "subjectKey": "001-003",
         "siteId": 2,
         "formKey": "AE",
         "intervalId": 15,
         "role": "Research Coordinator",
         "user": "jdoe",
         "reasonForChange": "Data entry error",
         "deleted": true,
         "dateCreated": "2025-06-05 21:12:09"
       }
     ]
   }

Response Fields
---------------

``metadata.status`` (String)
    HTTP status.
``metadata.method`` (String)
    HTTP method.
``metadata.path`` (String)
    Requested URI path.
``metadata.timestamp`` (String)
    Timestamp when response was generated.
``metadata.error`` (Object)
    Detailed error message if an error occurred.
``pagination.currentPage`` (Number)
    Current index page.
``pagination.size`` (Number)
    Size per page.
``pagination.totalPages`` (Number)
    Total pages returned from search.
``pagination.totalElements`` (Number)
    Total elements returned from search.
``pagination.sort[].property`` (String)
    Sort property.
``pagination.sort[].direction`` (String)
    Sort direction.
``data[].studyKey`` (String)
    Unique study key.
``data[].recordRevisionId`` (Number)
    Unique system identifier for the record revision.
``data[].recordId`` (Number)
    Unique system identifier for the related record.
``data[].recordOid`` (String)
    Client-assigned record OID.
``data[].recordRevision`` (Number)
    Record revision number.
``data[].dataRevision`` (Number)
    Data revision number.
``data[].recordStatus`` (String)
    User defined record status.
``data[].subjectId`` (Number)
    Mednet Subject ID.
``data[].subjectOid`` (String)
    Client-assigned subject OID.
``data[].subjectKey`` (String)
    Protocol-assigned subject identifier.
``data[].siteId`` (Number)
    Unique system identifier for the related site.
``data[].formKey`` (String)
    Form key.
``data[].intervalId`` (Number)
    Unique system identifier for the interval.
``data[].role`` (String)
    Role name of the user who saved the record revision.
``data[].user`` (String)
    Username of the user who saved the record revision.
``data[].reasonForChange`` (String)
    Record revision's Reason For Change data.
``data[].deleted`` (Boolean)
    Record deleted flag.
``data[].dateCreated`` (String)
    Date when this record revision was created.

Reference
---------

`Portal docs <https://portal.prod.imednetapi.com/docs/Record%20Revisions>`_
