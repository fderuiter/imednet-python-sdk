Codings Endpoint
================

The codings endpoint exposes medical coding activity for a study. Entries are
created when values collected in iMednet are standardized to a dictionary term
such as MedDRA.

Accessing the index
-------------------

A ``GET`` request returns the coding history for a study::

   GET /api/v1/edc/studies/PHARMADEMO/codings?page=0&size=25 \
       &sort=recordId%2CASC&filter=dictionaryName%3DMedDRA HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------

``studyKey``
   The study identifier used to retrieve codings.

Request parameters
------------------

``page``
   Index page to return. Defaults to ``0``.

``size``
   Items per page. Defaults to ``25`` with a maximum of ``500``.

``sort``
   Property used to sort results. Append ``asc`` or ``desc`` to specify the
   direction. Multiple ``sort`` parameters may be supplied. The default is
   ``formId,asc``.

``filter``
   Optional search criteria. See :doc:`../rest_api_reference` for syntax.

Response body
-------------

Example response::

   {
     "metadata": {
       "status": "OK",
       "method": "GET",
       "path": "/api/v1/edc/studies/PHARMADEMO/codings",
       "timestamp": "2025-06-05 21:12:10",
       "error": {}
     },
     "pagination": {
       "currentPage": 0,
       "size": 25,
       "totalPages": 1,
       "totalElements": 1,
       "sort": [
         {
           "property": "recordId",
           "direction": "ASC"
         }
       ]
     },
     "data": [
       {
         "studyKey": "PHARMADEMO",
         "siteName": "Chicago Hope Hospital",
         "siteId": 128,
         "subjectId": 247,
         "subjectKey": "111-005",
         "formId": 1,
         "formName": "Adverse Event",
         "formKey": "AE",
         "revision": 2,
         "recordId": 1,
         "variable": "AETERM",
         "value": "Angina",
         "codingId": 1,
         "code": "Angina agranulocytic",
         "codedBy": "John Smith",
         "reason": "Typo fix",
         "dictionaryName": "MedDRA",
         "dictionaryVersion": "24.0",
         "dateCoded": "2025-06-05 21:12:10"
       }
     ]
   }

Response fields
---------------

``metadata.status``
   HTTP status.

``metadata.method``
   HTTP method.

``metadata.path``
   Requested URI path.

``metadata.timestamp``
   Timestamp when the response was generated.

``metadata.error``
   Detail error message if the request failed.

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
   Unique study key for a given study.

``data[].siteName``
   Site name.

``data[].siteId``
   Unique site identifier.

``data[].subjectId``
   Mednet subject ID.

``data[].subjectKey``
   Protocol assigned subject identifier.

``data[].formId``
   Mednet form ID.

``data[].formName``
   Name of the eCRF.

``data[].formKey``
   Form key.

``data[].revision``
   Number of modifications of the coding metadata.

``data[].recordId``
   Unique record identifier.

``data[].variable``
   Name of the variable on the eCRF.

``data[].value``
   Value that was coded.

``data[].codingId``
   Mednet coding ID.

``data[].code``
   Assigned code.

``data[].codedBy``
   User who recorded the code.

``data[].reason``
   Reason the code was added.

``data[].dictionaryName``
   Dictionary name.

``data[].dictionaryVersion``
   Dictionary version.

``data[].dateCoded``
   Date the code was recorded.

`Portal docs <https://portal.prod.imednetapi.com/docs/codings>`_
