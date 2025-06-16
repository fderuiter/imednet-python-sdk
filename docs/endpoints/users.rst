Users Endpoint
==============

Given a StudyKey, fetch the users.

Accessing the index
-------------------
A ``GET`` request is used to access the index.

Request structure
-----------------

.. code-block:: http

   GET /api/v1/edc/studies/MOCK-STUDY/users?page=0&size=25&includeInactive=false&sort=login%2CASC HTTP/1.1
   Content-Type: application/json
   Host: localhost:8080

Path parameters
---------------
Path parameters are required.

``studyKey``
  StudyKey to retrieve list of variables.

Request parameters
------------------
Request parameters are optional. Default values are used unless specified.

``page``
  Which index page to be returned. Default value is ``0``.
``size``
  Items per page to be returned. Default value is ``25``. Maximum items allowed per page is ``500``.
``sort``
  Name of the property by which to sort the result set. To sort in a particular direction add a comma to the property name and either ``asc`` or ``desc``. To sort by multiple properties add additional sort parameters. Default value is ``login,asc``.
``includeInactive``
  Boolean flag whether to include inactive Users. Default value is ``false``.

Response body
-------------
Below is an example response payload.

.. code-block:: json

   {
     "metadata": {
       "status": "OK",
       "method": "GET",
       "path": "/api/v1/edc/studies/MOCK-STUDY/users",
       "timestamp": "2025-06-05 21:12:07",
       "error": {}
     },
     "pagination": {
       "currentPage": 0,
       "size": 25,
       "totalPages": 1,
       "totalElements": 1,
       "sort": [
         {
           "property": "login",
           "direction": "ASC"
         }
       ]
     },
     "data": [
       {
         "userId": "685253e1-1a95-4352-a7b0-4c62d3807727",
         "login": "wsmith1",
         "firstName": "William",
         "lastName": "Smith",
         "email": "wsmith@mednet.com",
         "userActiveInStudy": true,
         "roles": [
           {
             "dateCreated": [2025, 6, 5, 21, 12, 7, 625000000],
             "dateModified": [2025, 6, 5, 21, 12, 7, 625000000],
             "roleId": "6ec2a32b-143c-43d3-b562-9d902a61f884",
             "communityId": 1,
             "name": "Role name 1",
             "description": "Role description 1",
             "level": 1,
             "type": "Role type 1",
             "inactive": false
           },
           {
             "dateCreated": [2025, 6, 5, 21, 12, 7, 625000000],
             "dateModified": [2025, 6, 5, 21, 12, 7, 625000000],
             "roleId": "6ec2a32b-143c-43d3-b562-9d902a61f884",
             "communityId": 2,
             "name": "Role name 2",
             "description": "Role description 2",
             "level": 2,
             "type": "Role type 2",
             "inactive": false
           }
         ]
       }
     ]
   }

Response fields
---------------

``metadata.status``
  String - HTTP status.
``metadata.method``
  String - HTTP method.
``metadata.path``
  String - Requested URI path.
``metadata.timestamp``
  String - Timestamp when response was generated.
``metadata.error``
  Object - Detail error message from request if error occur.
``pagination.currentPage``
  Number - Current index page.
``pagination.size``
  Number - Size per page.
``pagination.totalPages``
  Number - Total pages return from search.
``pagination.totalElements``
  Number - Total elements return from search.
``pagination.sort[].property``
  String - Sort property.
``pagination.sort[].direction``
  String - Sort direction.
``data[].userId``
  String - User ID.
``data[].login``
  String - Login.
``data[].firstName``
  String - First name.
``data[].lastName``
  String - Last name.
``data[].email``
  String - Email.
``data[].userActiveInStudy``
  Boolean - Boolean value for if the user is active in the study.
``data[].roles[].dateCreated``
  Array - Role date created.
``data[].roles[].dateModified``
  Array - Role date modified.
``data[].roles[].roleId``
  String - Role ID.
``data[].roles[].communityId``
  Number - Community ID associated with Role.
``data[].roles[].name``
  String - Role name.
``data[].roles[].description``
  String - Role description.
``data[].roles[].level``
  Number - Role level.
``data[].roles[].type``
  String - Role type.
``data[].roles[].inactive``
  Boolean - Inactive.

`Portal docs <https://portal.prod.imednetapi.com/docs/users>`_
