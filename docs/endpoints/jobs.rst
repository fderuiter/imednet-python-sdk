Jobs Endpoint
=============

Given a batch ID, fetch the job information created by a background operation.
Jobs are typically generated when you submit records via ``POST`` and the server
processes them asynchronously.

Accessing the job
-----------------

A ``GET`` request retrieves the job status.

.. code-block:: http

    GET /api/v1/edc/studies/MOCK-STUDY/jobs/f89ceda2-f7c8-4939-859e-d3e967f315a1 HTTP/1.1
    Content-Type: application/json
    Host: localhost:8080

Path parameters
---------------

All parameters in the path are required.

.. list-table:: /api/v1/edc/studies/{studyKey}/jobs/{batchId}
   :header-rows: 1

   * - Parameter
     - Description
   * - ``studyKey``
     - Study key used to look up the job state.
   * - ``batchId``
     - Batch ID returned from the ``POST /records`` request.

Example response
----------------

.. code-block:: json

    {
      "jobId": "930720e7-4f3b-4452-be2b-f4233e5f433b",
      "batchId": "9e9e8584-0c71-40f2-86ee-7d414766f7f2",
      "state": "completed",
      "dateCreated": "2020-12-01 21:47:36",
      "dateStarted": "2020-12-01 21:47:42",
      "dateFinished": "2020-12-01 21:47:45"
    }

Response fields
---------------

.. list-table::
   :header-rows: 1

   * - Field
     - Type
     - Description
   * - ``jobId``
     - string
     - Job identifier
   * - ``batchId``
     - string
     - Associated batch ID
   * - ``state``
     - string
     - Current job state
   * - ``dateCreated``
     - string
     - Timestamp when the job was created
   * - ``dateStarted``
     - string
     - Timestamp when processing started
   * - ``dateFinished``
     - string
     - Timestamp when processing completed

`Portal docs <https://portal.prod.imednetapi.com/docs/jobs>`_
