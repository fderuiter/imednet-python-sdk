Variables Endpoint
==================

This endpoint retrieves the set of variables for a given study. Each variable
represents a field on an electronic clinical case report form (eCRF). Records in
the system contain responses for these variables within their ``recordData``
sections.

Accessing the index
-------------------

The list of variables is returned via a ``GET`` request.

Request structure
-----------------

.. code-block::

   GET /api/v1/edc/studies/PHARMADEMO/variables?page=0&size=25&sort=variableId%2CASC&
       filter=variableId%3D%3D10299 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------

``studyKey``
    Study key used to retrieve the list of variables. This value is required.

Request parameters
------------------

``page``
    Index page to return. Defaults to ``0``.

``size``
    Number of items per page. Defaults to ``25`` and may not exceed ``500``.

``sort``
    Property name to sort by. Append ``asc`` or ``desc`` to specify direction.
    Multiple ``sort`` parameters may be supplied. Defaults to ``formId,asc``.

``filter``
    Optional filter criteria. Must follow the API filter syntax.

Example response
----------------

.. code-block:: json

   {
     "metadata": {
       "status": "OK",
       "method": "GET",
       "path": "/api/v1/edc/studies/PHARMADEMO/variables",
       "timestamp": "2025-06-05 21:12:08",
       "error": {}
     },
     "pagination": {
       "currentPage": 0,
       "size": 25,
       "totalPages": 1,
       "totalElements": 1,
       "sort": [
         {
           "property": "variableId",
           "direction": "ASC"
         }
       ]
     },
     "data": [
       {
         "studyKey": "PHARMADEMO",
         "variableId": 1,
         "variableType": "RADIO",
         "variableName": "Pain Level",
         "sequence": 1,
         "revision": 1,
         "disabled": false,
         "dateCreated": "2025-06-05 21:12:08",
         "dateModified": "2025-06-05 21:12:09",
         "formId": 108727,
         "variableOid": "OID-1",
         "deleted": false,
         "formKey": "FORM_1",
         "formName": "Pre-procedure screening",
         "label": "Select patient pain level between 1 and 10",
         "blinded": false
       }
     ]
   }

Response fields
---------------

``metadata``
    Response metadata including HTTP status, method and timestamp.

``pagination``
    Information about the current page, page size, total pages and sort order.

``data``
    List of variables and their attributes for the specified study.
