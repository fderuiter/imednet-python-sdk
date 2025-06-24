Studies Endpoint
================

The ``/api/v1/edc/studies`` endpoint returns metadata for studies that the API
key is authorized to access.

Accessing the index
-------------------

Send a ``GET`` request to ``/api/v1/edc/studies``. Optional query parameters
control pagination, sorting and filtering.

Example::

    GET /api/v1/edc/studies?page=0&size=25&sort=studyKey%2CASC \
        &filter=studyKey%3D%3DPHARMADEMO HTTP/1.1
    x-imn-security-key: my-security-key
    x-api-key: my-api-token
    Content-Type: application/json
    Host: localhost:8080

Request parameters
------------------

``page``
    Index page to return. Defaults to ``0``.

``size``
    Items per page. Defaults to ``25`` with a maximum of ``500``.

``sort``
    Sort property and optional direction. Defaults to ``studyKey,asc``. Provide
    multiple ``sort`` parameters to sort by several properties.

``filter``
    Optional filter expression. See :doc:`../rest_api_reference` for syntax.

Response body
-------------

.. code-block:: json

    {
      "metadata": {
        "status": "OK",
        "method": "GET",
        "path": "/api/v1/edc/studies",
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
            "property": "studyKey",
            "direction": "ASC"
          }
        ]
      },
      "data": [
        {
          "sponsorKey": "100",
          "studyKey": "PHARMADEMO",
          "studyId": 100,
          "studyName": "iMednet Pharma Demonstration Study",
          "studyDescription": "iMednet Demonstration Study v2 Created 05April2018 After A5 Release",
          "studyType": "STUDY",
          "dateCreated": "2025-06-05 21:12:08",
          "dateModified": "2025-06-05 21:12:09"
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
    Error details if the request failed.

``pagination.currentPage``
    Current result page.

``pagination.size``
    Size per page.

``pagination.totalPages``
    Total pages returned.

``pagination.totalElements``
    Total elements returned.

``pagination.sort[].property``
    Sort property.

``pagination.sort[].direction``
    Sort direction.

``data[].sponsorKey``
    Sponsor key the study belongs to.

``data[].studyKey``
    Unique study key.

``data[].studyId``
    Mednet study ID.

``data[].studyName``
    Study name.

``data[].studyDescription``
    Study description.

``data[].studyType``
    Study type.

``data[].dateCreated``
    Record creation timestamp.

``data[].dateModified``
    Last modified timestamp.

`Portal docs <https://portal.prod.imednetapi.com/docs/studies>`_
