Queries Endpoint
================

Given a ``studyKey`` fetch the set of queries. A query is a conduct resource that
encapsulates dialogue pertaining to specific eCRF responses or other matters
relevant to the conduct of the study. Queries may be user‑initiated, or
automatically applied according to study protocol criteria.

Accessing the index
-------------------

A ``GET`` request is used to access the index.

Request structure
-----------------

.. code-block:: http

   GET /api/v1/edc/studies/batchId/queries?page=0&size=25&sort=annotationId%2CASC&filter=variable%3D%3Daeterm HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
~~~~~~~~~~~~~~~

``studyKey``
    StudyKey to retrieve list of query.

Request parameters
~~~~~~~~~~~~~~~~~~

``page``
    Which index page to be returned. Default value is ``0``.

``size``
    Items per page to be returned. Default value is ``25``. Maximum items allowed
    per page is ``500``.

``sort``
    Name of the property by which to sort the result set. To sort in a particular
    direction add a comma to the property name and either ``asc`` or ``desc``.
    To sort by multiple properties add additional ``sort`` parameters. Default
    value is ``annotationId,asc``.

``filter``
    Optional filter search criteria. Must follow correct syntax. Refer to
    :doc:`../rest_api_reference` for details.

Response body
-------------

Below is an example response payload.

.. code-block:: json

   {
     "metadata" : {
       "status" : "OK",
       "method" : "GET",
       "path" : "/api/v1/edc/studies/batchId/queries",
       "timestamp" : "2025-06-05 21:12:09",
       "error" : { }
     },
     "pagination" : {
       "currentPage" : 0,
       "size" : 25,
       "totalPages" : 1,
       "totalElements" : 1,
       "sort" : [ {
         "property" : "annotationId",
         "direction" : "ASC"
       } ]
     },
     "data" : [ {
       "studyKey" : "PHARMADEMO",
       "subjectId" : 1,
       "subjectOid" : "OID-1",
       "annotationType" : "subject",
       "annotationId" : 1,
       "type" : null,
       "description" : "Monitor Query",
       "recordId" : 123,
       "variable" : "aeterm",
       "subjectKey" : "123-005",
       "dateCreated" : "2025-06-05 21:12:09",
       "dateModified" : "2025-06-05 21:12:10",
       "queryComments" : [ {
         "sequence" : 1,
         "annotationStatus" : "Monitor Query Open",
         "user" : "john",
         "comment" : "Added comment to study",
         "closed" : false,
         "date" : "2025-06-05 21:12:09"
       } ]
     } ]
   }

Response fields
---------------

``metadata.status``
    Http status

``metadata.method``
    Http method

``metadata.path``
    Requested URI path

``metadata.timestamp``
    Timestamp when response was generated

``metadata.error``
    Detail error message from request if error occur

``pagination.currentPage``
    Current index page

``pagination.size``
    Size per page

``pagination.totalPages``
    Total pages return from search

``pagination.totalElements``
    Total elements return from search

``pagination.sort[].property``
    Sort property

``pagination.sort[].direction``
    Sort direction

``data[].studyKey``
    Unique study key for a given study

``data[].subjectId``
    Mednet Subject ID

``data[].subjectOid``
    Client-assigned subject OID

``data[].annotationType``
    User defined identifier for Query Type

``data[].annotationId``
    Unique system identifier for Query Instance

``data[].type``
    System text identifier for query type/location. Valid responses are
    ``subject`` | ``record`` | ``question``

``data[].description``
    Query description

``data[].subjectKey``
    Protocol-assigned subject identifier

``data[].recordId``
    Unique system identifier for Record

``data[].variable``
    User defined field identifier

``data[].queryComments[].sequence``
    Query sequence

``data[].queryComments[].user``
    User performing Query action

``data[].queryComments[].annotationStatus``
    User defined Query status

``data[].queryComments[].comment``
    User comments applied at time of Query action

``data[].queryComments[].closed``
    Query moved to closed status

``data[].queryComments[].date``
    Date of Query Comment

``data[].dateCreated``
    Date when the query was created

``data[].dateModified``
    Date when the query was modified

`Portal docs <https://portal.prod.imednetapi.com/docs/queries>`_
