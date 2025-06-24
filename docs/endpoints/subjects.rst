Subjects Endpoint
=================

Given a ``studyKey`` this endpoint returns all subjects for the study. A subject represents
one participant and belongs to exactly one site. Each subject may have multiple records.

Accessing the index
-------------------

Send a ``GET`` request to ``/api/v1/edc/studies/{studyKey}/subjects``.

Example::

   GET /api/v1/edc/studies/PHARMADEMO/subjects?page=0&size=25&sort=subjectId%2CASC&filter=subjectId%3D%3D370 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------

``studyKey``
  Study key to retrieve subjects for.

Request parameters
------------------

``page``
  Index page to return. Defaults to ``0``.

``size``
  Items per page. Defaults to ``25`` with a maximum of ``500``.

``sort``
  Sort property and direction separated by a comma. Defaults to ``subjectId,asc``.

``filter``
  Optional filter expression. See the :doc:`../rest_api_reference` for syntax.

Response body
-------------

Example payload::

   {
     "metadata": {
       "status": "OK",
       "method": "GET",
       "path": "/api/v1/edc/studies/PHARMADEMO/subjects",
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
           "property": "subjectId",
           "direction": "ASC"
         }
       ]
     },
     "data": [
       {
         "studyKey": "PHARMADEMO",
         "subjectId": 1,
         "subjectOid": "OID-1",
         "subjectKey": "01-001",
         "subjectStatus": "Enrolled",
         "siteId": 128,
         "siteName": "Chicago Hope Hospital",
         "deleted": false,
         "enrollmentStartDate": "2025-06-05 21:12:09",
         "dateCreated": "2025-06-05 21:12:09",
         "dateModified": "2025-06-05 21:12:10",
         "keywords": [
           {
             "keywordName": "Data Entry Error",
             "keywordKey": "DEE",
             "keywordId": 15362,
             "dateAdded": "2025-06-05 21:12:09"
           }
         ]
       }
     ]
   }

Response fields
---------------

``metadata.status`` (String)
  HTTP status.

``metadata.method`` (String)
  HTTP method.

``metadata.path`` (String)
  Request path.

``metadata.timestamp`` (String)
  Timestamp when the response was generated.

``metadata.error`` (Object)
  Detailed error information when a request fails.

``pagination.currentPage`` (Number)
  Current index page.

``pagination.size`` (Number)
  Page size returned.

``pagination.totalPages`` (Number)
  Total pages in the result set.

``pagination.totalElements`` (Number)
  Total elements found.

``pagination.sort[].property`` (String)
  Sort property.

``pagination.sort[].direction`` (String)
  Sort direction.

``data[].studyKey`` (String)
  Unique study key for a given study.

``data[].subjectId`` (Number)
  Mednet subject ID.

``data[].subjectOid`` (String)
  Client assigned subject OID.

``data[].subjectKey`` (String)
  Protocol assigned subject identifier.

``data[].subjectStatus`` (String)
  Subject status.

``data[].siteId`` (Number)
  Mednet site ID.

``data[].siteName`` (String)
  Site name.

``data[].enrollmentStartDate`` (String)
  Enrollment start date.

``data[].deleted`` (Boolean)
  Subject deleted flag.

``data[].dateCreated`` (String)
  Date the subject was created.

``data[].dateModified`` (String)
  Last modification date.

``data[].keywords`` (Array)
  Keywords associated with the subject.

`Portal docs <https://portal.prod.imednetapi.com/docs/subjects>`_
