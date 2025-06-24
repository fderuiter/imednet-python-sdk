Sites Endpoint
==============

Given a ``studyKey``, fetch the set of sites. A site is a conduct resource that
represents a single hospital, clinic, or other type of geographic entity which
will contain subjects that participate in the study.

Sites are related to subjects in that any site has one-to-many subjects.

Accessing the index
-------------------

A ``GET`` request is used to access the index.

.. code-block::

   GET /api/v1/edc/studies/PHARMADEMO/sites?page=0&size=25&sort=siteId%2CASC \
     &filter=siteId%3D%3D48 HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------

Path parameters are required.

``/api/v1/edc/studies/{studyKey}/sites``

:studyKey: StudyKey to retrieve list of sites that belong to particular study.

Request parameters
------------------

Request parameters are optional. Default values are used unless specified.

:page: Which index page to be returned. Default value is 0.
:size: Items per page to be returned. Default value is 25. Maximum items
       allowed per page is 500.
:sort: Name of the property by which to sort the result set. To sort in a
       particular direction add a comma to the property name and either
       ``asc`` or ``desc``. To sort by multiple properties add additional sort
       parameters. Default value is ``siteId,asc``.
:filter: Optional filter search criteria. Must follow correct syntax. Refer to
         :doc:`../rest_api_reference` for details.

Response body
-------------

Below is an example response payload.

.. code-block:: json

   {
     "metadata" : {
       "status" : "OK",
       "method" : "GET",
       "path" : "/api/v1/edc/studies/PHARMADEMO/sites",
       "timestamp" : "2025-06-05 21:12:09",
       "error" : { }
     },
     "pagination" : {
       "currentPage" : 0,
       "size" : 25,
       "totalPages" : 1,
       "totalElements" : 1,
       "sort" : [ {
         "property" : "siteId",
         "direction" : "ASC"
       } ]
     },
     "data" : [ {
       "studyKey" : "PHARMADEMO",
       "siteId" : 1,
       "siteName" : "Mock Site 1",
       "siteEnrollmentStatus" : "Enrollment Open",
       "dateCreated" : "2025-06-05 21:12:09",
       "dateModified" : "2025-06-05 21:12:10"
     } ]
   }

Response fields
---------------

The table below describes each field in the response.

.. list-table::
   :header-rows: 1

   * - Path
     - Type
     - Description
   * - ``metadata.status``
     - String
     - HTTP status
   * - ``metadata.method``
     - String
     - HTTP method
   * - ``metadata.path``
     - String
     - Requested URI path
   * - ``metadata.timestamp``
     - String
     - Timestamp when response was generated
   * - ``metadata.error``
     - Object
     - Detail error message from request if error occur
   * - ``pagination.currentPage``
     - Number
     - Current index page
   * - ``pagination.size``
     - Number
     - Size per page
   * - ``pagination.totalPages``
     - Number
     - Total pages return from search
   * - ``pagination.totalElements``
     - Number
     - Total elements return from search
   * - ``pagination.sort[].property``
     - String
     - Sort property
   * - ``pagination.sort[].direction``
     - String
     - Sort direction
   * - ``data[].studyKey``
     - String
     - Unique study key for a given study
   * - ``data[].siteId``
     - Number
     - Unique site Id
   * - ``data[].siteName``
     - String
     - Site name
   * - ``data[].siteEnrollmentStatus``
     - String
     - Status of site enrollment
   * - ``data[].dateCreated``
     - String
     - Date when this record was created
   * - ``data[].dateModified``
     - String
     - Last date modified of this record

`Portal docs <https://portal.prod.imednetapi.com/docs/sites>`_
