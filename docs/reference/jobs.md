# Jobs Endpoint Documentation

## Overview

The **Jobs Endpoint** allows users to retrieve the status and details of a specific **job** using a `batchId`. A **job** represents an API operation created by submitting a request to the **POST** Records Endpoint.

---

## Accessing the Index

To retrieve job information, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/MOCK-STUDY/jobs/1601b8a0-45ba-4136-8c55-17fab704bc80 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                      |
|-------------|--------------------------------------------------|
| `studyKey`  | Study Key to retrieve job state                  |
| `batchId`   | Batch ID returned from the **POST** Records endpoint |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/jobs/{batchId}
```

---

## Response Body

### Example Response

```json
{
  "jobId": "afa2d61e-07ed-4efe-99c5-6f358f5e7d38",
  "batchId": "75e63db6-fa41-40bc-b939-cf3bdb246ae8",
  "state": "completed",
  "dateCreated": "2020-12-01 21:47:36",
  "dateStarted": "2020-12-01 21:47:42",
  "dateFinished": "2020-12-01 21:47:45"
}
```

---

## Response Fields

| Path             | Type    | Description                                    |
|------------------|---------|------------------------------------------------|
| `jobId`          | String  | Unique identifier for the job                  |
| `batchId`        | String  | Batch ID linked to the submitted job           |
| `state`          | String  | Current state of the job (`created`, `running`, `completed`, `failed`) |
| `dateCreated`    | String  | Timestamp when the job was created             |
| `dateStarted`    | String  | Timestamp when the job started processing      |
| `dateFinished`   | String  | Timestamp when the job completed processing    |

---

## Example Usage

### **Checking the Status of a Job**

To check the status of a job with `batchId = 75e63db6-fa41-40bc-b939-cf3bdb246ae8` in the study `MOCK-STUDY`:

```http
GET /api/v1/edc/studies/MOCK-STUDY/jobs/75e63db6-fa41-40bc-b939-cf3bdb246ae8 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Possible Job States

| State       | Description                                                     |
|-------------|-----------------------------------------------------------------|
| `created`   | Job has been created but not yet started.                       |
| `running`   | Job is currently being processed.                               |
| `completed` | Job has completed successfully.                                 |
| `failed`    | Job encountered an error during processing.                     |

---

## Notes

- **Job Tracking:**
  - Jobs allow for asynchronous processing of submitted records, enabling users to track the status over time.

- **Timestamps:**
  - All timestamps are in the format `YYYY-MM-DD HH:MM:SS` and represent UTC time unless otherwise noted.

- **Error Handling:**
  - If a job fails, further details can be retrieved using the associated `jobId` in error-specific endpoints (if available).

---
