Records Endpoint
================

Given a ``studyKey``, fetch the set of records. A record is a conduct resource that
represents a single instance of an electronic case report form (eCRF). Each record
contains the responses to each question on the eCRF.

Accessing the index
-------------------

A ``GET`` request retrieves records while ``POST`` adds records to the iMednet
database.

Path parameters
---------------

``{studyKey}``
  StudyKey to retrieve list of records.

GET Requests
------------

.. code-block::


   GET /api/v1/edc/studies/PHARMADEMO/records?page=0&size=25&sort=recordId%2CASC&filter=recordId%3D%3D5510&recordDataFilter=aeterm%3D%3DBronchitis HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

**GET Request parameters**

Request parameters are optional. Default values are used unless specified.


``page``
    Which index page to be returned. Default value is ``0``.

``size``
    Items per page to be returned. Default value is ``25``. Maximum items allowed per page is ``500``.

``sort``
    Name of the property by which to sort the result set. To sort in a particular
    direction add a comma to the property name and ``asc`` or ``desc``. To sort by
    multiple properties add additional sort parameters. Default value is ``recordId,asc``.

``filter``
    Optional filter search criteria. Must follow correct syntax. Refer to
    :doc:`../rest_api_reference` for details.

``recordDataFilter``
    Optional record data filter search criteria. Must follow correct syntax. Refer to
    :doc:`../rest_api_reference` for details.

**GET Response body**

.. code-block:: json

   {
     "metadata" : {
       "status" : "OK",
       "method" : "GET",
       "path" : "/api/v1/edc/studies/PHARMADEMO/records",
       "timestamp" : "2025-06-05 21:12:09",
       "error" : { }
     },
     "pagination" : {
       "currentPage" : 0,
       "size" : 25,
       "totalPages" : 1,
       "totalElements" : 1,
       "sort" : [ {
         "property" : "recordId",
         "direction" : "ASC"
       } ]
     },
     "data" : [ {
       "studyKey" : "PHARMADEMO",
       "intervalId" : 99,
       "formId" : 10202,
       "formKey" : "AE",
       "siteId" : 128,
       "recordId" : 1,
       "recordOid" : "REC-1",
       "recordType" : "SUBJECT",
       "recordStatus" : "Record Incomplete",
       "deleted" : false,
       "dateCreated" : "2025-06-05 21:12:09",
       "dateModified" : "2025-06-05 21:12:10",
       "subjectId" : 326,
       "subjectOid" : "OID-1",
       "subjectKey" : "123-456",
       "visitId" : 1,
       "parentRecordId" : 34,
       "keywords" : [ {
         "keywordName" : "Data Entry Error",
         "keywordKey" : "DEE",
         "keywordId" : 15362,
         "dateAdded" : "2025-06-05 21:12:09"
       } ],
       "recordData" : {
         "dateCreated" : "2018-10-18 06:21:46",
         "unvnum" : "1",
         "dateModified" : "2018-11-18 07:11:16",
         "aeser" : "",
         "aeterm" : "Bronchitis"
       }
     } ]
   }

**GET Response fields**
The JSON response includes three sections:

- ``metadata`` describing the status, request path and timestamp.
- ``pagination`` information about page numbers and sort order.
- ``data`` containing a list of record objects.


POST Requests
-------------

Providing a ``studyKey`` and a request body adds a record to the iMednet database.
The request body is an array. The contents of the body determine if the request
will register a subject, update a scheduled record, or create a new record.

**Request structure**

.. code-block::

   POST /api/v1/edc/studies/PHARMADEMO/records HTTP/1.1
   x-email-notify: user@domain.com
   Accept: application/json
   Content-Type: application/json
   Host: localhost:8080

   [ ]

**POST Request Identifiers**

``formKey``
    User defined form key.
``formId``
    System generated form identifier.
``siteName``
    User defined site name.
``siteId``
    System generated site identifier.
``subjectKey``
    Patient Display ID Full.
``subjectId``
    System generated subject identifier.
``subjectOid``
    User assigned subject OID.
``intervalName``
    User defined interval name.
``intervalId``
    System generated interval identifier.
``recordId``
    System generated record identifier.
``recordOid``
    User defined record OID.

**Field Types**

When making a POST request, use the correct type for any fields included in the
``data`` object.

Sample request body containing all valid field types:

.. code-block:: json

   [ {
     "formKey" : "REG",
     "siteName" : "Minneapolis",
     "data" : {
       "textField" : "Text data",
       "dateField" : "2020-01-20",
       "numberField" : 11,
       "radioField" : "Yes",
       "dropdownField" : "Always",
       "memoField" : "Memo data",
       "checkboxField" : true
     }
   } ]

Valid field types:

+---------------------------+---------+-------------------------------+
| Path                      | Type    | Description                   |
+===========================+=========+===============================+
| ``[].formKey``            | String  | Form Key                      |
+---------------------------+---------+-------------------------------+
| ``[].siteName``           | String  | Site Name                     |
+---------------------------+---------+-------------------------------+
| ``[].data``               | Object  | Data for specific record      |
+---------------------------+---------+-------------------------------+
| ``[].data.textField``     | String  | Text field                    |
+---------------------------+---------+-------------------------------+
| ``[].data.dateField``     | String  | Date field                    |
+---------------------------+---------+-------------------------------+
| ``[].data.numberField``   | Number  | Number field                  |
+---------------------------+---------+-------------------------------+
| ``[].data.radioField``    | String  | Radio field                   |
+---------------------------+---------+-------------------------------+
| ``[].data.dropdownField`` | String  | Dropdown field                |
+---------------------------+---------+-------------------------------+
| ``[].data.memoField``     | String  | Memo field                    |
+---------------------------+---------+-------------------------------+
| ``[].data.checkboxField`` | Boolean | Checkbox field                |
+---------------------------+---------+-------------------------------+

Register Subject
----------------

Request body for registering a subject:

.. code-block:: json

   [ {
     "formKey" : "REG",
     "siteName" : "Minneapolis",
     "data" : {
       "textField" : "Text value"
     }
   } ]

Request fields:

+-----------------------+---------+-------------------------------+
| Path                  | Type    | Description                   |
+=======================+=========+===============================+
| ``[].formKey``        | String  | Form Key                      |
+-----------------------+---------+-------------------------------+
| ``[].siteName``       | String  | Site Name                     |
+-----------------------+---------+-------------------------------+
| ``[].data``           | Object  | Data for specific record      |
+-----------------------+---------+-------------------------------+
| ``[].data.textField`` | String  | Text field                    |
+-----------------------+---------+-------------------------------+

Update a Scheduled Record
-------------------------

Request body for updating a scheduled record:

.. code-block:: json

   [ {
     "formKey" : "REG",
     "subjectKey" : "651-042",
     "intervalName" : "Registration",
     "data" : {
       "textField" : "Text value"
     }
   } ]

Request fields:

+-----------------------+---------+-------------------------------+
| Path                  | Type    | Description                   |
+=======================+=========+===============================+
| ``[].formKey``        | String  | Form Key                      |
+-----------------------+---------+-------------------------------+
| ``[].subjectKey``     | String  | Subject Key                   |
+-----------------------+---------+-------------------------------+
| ``[].intervalName``   | String  | Interval Name                 |
+-----------------------+---------+-------------------------------+
| ``[].data``           | Object  | Data for specific record      |
+-----------------------+---------+-------------------------------+
| ``[].data.textField`` | String  | Text field                    |
+-----------------------+---------+-------------------------------+

Create a New Record
-------------------

Request body for creating a new record:

.. code-block:: json

   [ {
     "formKey" : "REG",
     "subjectKey" : "123-876",
     "data" : {
       "textField" : "Text value"
     }
   } ]

Request fields:

+-----------------------+---------+-------------------------------+
| Path                  | Type    | Description                   |
+=======================+=========+===============================+
| ``[].formKey``        | String  | Form Key                      |
+-----------------------+---------+-------------------------------+
| ``[].subjectKey``     | String  | Subject Key                   |
+-----------------------+---------+-------------------------------+
| ``[].data``           | Object  | Data for specific record      |
+-----------------------+---------+-------------------------------+
| ``[].data.textField`` | String  | Text field                    |
+-----------------------+---------+-------------------------------+

Response body
-------------

The POST request returns a ``batchId`` and a ``state`` which can be used to check
on the status of the record being added via ``GET`` requests to the jobs
endpoint.

.. code-block:: json

   {
     "jobId": "9663fe34-eec7-460a-a820-097f1eb2875e",
     "batchId" : "c3q191e4-f894-72cd-a753-b37283eh0866",
     "state": "created"
   }

`Portal docs <https://portal.prod.imednetapi.com/docs/records>`_
