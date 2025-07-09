Visits Endpoint
===============

Given a ``studyKey``, fetch the set of visits for that study. A visit represents a single
instance of an interval for a subject.

Accessing the index
-------------------

A ``GET`` request is used to access the index.

Request structure
-----------------

.. code-block:: http

   GET /api/v1/edc/studies/PHARMADEMO/visits?page=0&size=25&sort=visitId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------

Path parameters are required.

.. list-table:: /api/v1/edc/studies/{studyKey}/visits
   :header-rows: 1

   * - Parameter
     - Description
   * - ``studyKey``
     - StudyKey to retrieve list of visits

Request parameters
------------------

Request parameters are optional. Default values are used unless specified.

.. list-table::
   :header-rows: 1

   * - Parameter
     - Description
   * - ``page``
     - Which index page to be returned. Default value is 0.
   * - ``size``
     - Items per page to be returned. Default value is 25. Maximum items allowed per page is 500
   * - ``sort``
     - Name of the property by which to sort the result set. To sort in a particular direction add a comma to the property name and either ``asc`` or ``desc``. To sort by multiple properties add additional sort parameters. Default value is ``visitId,asc``.
   * - ``filter``
     - Optional filter search criteria. Must follow correct syntax. Refer to filter section for details.

Response body
-------------

Below is an example response payload.

.. code-block:: json

   {
     "metadata" : {
       "status" : "OK",
       "method" : "GET",
       "path" : "/api/v1/edc/studies/PHARMADEMO/visits",
       "timestamp" : "2025-06-05 21:12:08",
       "error" : { }
     },
     "pagination" : {
       "currentPage" : 0,
       "size" : 25,
       "totalPages" : 1,
       "totalElements" : 1,
       "sort" : [ {
         "property" : "visitId",
         "direction" : "ASC"
       } ]
     },
     "data" : [ {
       "visitId" : 1,
       "studyKey" : "PHARMADEMO",
       "intervalId" : 13,
       "intervalName" : "Day 15",
       "subjectId" : 247,
       "subjectKey" : "111-005",
       "startDate" : "2025-06-05",
       "endDate" : "2025-06-12",
       "dueDate" : null,
       "visitDate" : "2025-06-07",
       "visitDateForm" : "Follow Up",
       "deleted" : false,
       "visitDateQuestion" : "AESEV",
       "dateCreated" : "2025-06-05 21:12:08",
       "dateModified" : "2025-06-05 21:12:08"
     } ]
   }

Response fields
---------------

.. list-table::
   :header-rows: 1

   * - Path
     - Type
     - Description
   * - ``metadata.status``
     - String
     - Http status
   * - ``metadata.method``
     - String
     - Http method
   * - ``metadata.path``
     - String
     - Requested URI path
   * - ``metadata.timestamp``
     - String
     - Timestamp when response was generated
   * - ``metadata.error``
     - Object
     - Detailed error message from request if an error occurred
   * - ``pagination.currentPage``
     - Number
     - Current index page
   * - ``pagination.size``
     - Number
     - Size per page
   * - ``pagination.totalPages``
     - Number
     - Total pages returned from search
   * - ``pagination.totalElements``
     - Number
     - Total elements returned from search
   * - ``pagination.sort[].property``
     - String
     - Sort property
   * - ``pagination.sort[].direction``
     - String
     - Sort direction
   * - ``data[].studyKey``
     - String
     - Unique study key for a given study
   * - ``data[].subjectId``
     - Number
     - Mednet Subject ID
   * - ``data[].subjectKey``
     - String
     - Protocol-assigned subject identifier
   * - ``data[].visitId``
     - Number
     - Unique system identifier for the subject visit instance
   * - ``data[].intervalId``
     - Number
     - Unique system identifier for the related interval
   * - ``data[].intervalName``
     - String
     - User defined identifier for the related interval
   * - ``data[].startDate``
     - String
     - Subject visit Start Date defined in interval visit window
   * - ``data[].dueDate``
     - Null
     - Subject visit Due Date defined in interval visit window
   * - ``data[].endDate``
     - String
     - Subject visit End Date defined in interval visit window
   * - ``data[].visitDate``
     - String
     - Subject visit Actual Date defined in interval visit window
   * - ``data[].visitDateForm``
     - String
     - Actual Date Form defined in interval visit window
   * - ``data[].deleted``
     - Boolean
     - Subject visit deleted flag
   * - ``data[].visitDateQuestion``
     - String
     - User defined field identifier
   * - ``data[].dateCreated``
     - String
     - Date when this visit was created
   * - ``data[].dateModified``
     - String
     - Date when this visit was last modified

`Portal docs <https://portal.prod.imednetapi.com/docs/visits>`_
