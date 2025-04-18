# Record Revisions Endpoint Documentation

## Overview

The **Record Revisions Endpoint** allows users to fetch the set of **record revisions** for a given `StudyKey`. A **record revision** represents a distinct state or version in the lifecycle of a record. Each record may have multiple revisions, captured whenever data is modified or the record progresses to a new status.

---

## Accessing the Index

To retrieve record revisions, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/recordRevisions?page=0&size=25&sort=recordRevisionId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                  |
|-------------|----------------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of record revisions |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/recordRevisions
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                              |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                    |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                     |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `recordRevisionId,asc`. |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                       |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/recordRevisions",
    "timestamp": "2024-11-04 16:03:19",
    "error": {}
  },
  "pagination": {
    "currentPage": 0,
    "size": 25,
    "totalPages": 1,
    "totalElements": 1,
    "sort": [
      {
        "property": "recordRevisionId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "recordRevisionId": 1,
      "recordId": 1,
      "recordOid": "REC-1",
      "recordRevision": 1,
      "dataRevision": 1,
      "recordStatus": "Record Complete",
      "subjectId": 247,
      "subjectOid": "OID-1",
      "subjectKey": "001-003",
      "siteId": 2,
      "formKey": "AE",
      "intervalId": 15,
      "role": "Research Coordinator",
      "user": "jdoe",
      "reasonForChange": "Data entry error",
      "deleted": true,
      "dateCreated": "2024-11-04 16:03:19"
    }
  ]
}
```

---

## Response Fields

### **Metadata**

| Path                  | Type    | Description                                      |
|-----------------------|---------|--------------------------------------------------|
| `metadata.status`     | String  | HTTP status                                      |
| `metadata.method`     | String  | HTTP method used                                 |
| `metadata.path`       | String  | Requested URI path                               |
| `metadata.timestamp`  | String  | Timestamp when the response was generated        |
| `metadata.error`      | Object  | Detailed error message if an error occurred      |

---

### **Pagination**

| Path                        | Type    | Description                                    |
|-----------------------------|---------|------------------------------------------------|
| `pagination.currentPage`    | Number  | Current page index                             |
| `pagination.size`           | Number  | Number of items per page                       |
| `pagination.totalPages`     | Number  | Total number of pages                          |
| `pagination.totalElements`  | Number  | Total number of elements                       |
| `pagination.sort[].property`| String  | Property used for sorting                      |
| `pagination.sort[].direction`| String | Sorting direction (`ASC` or `DESC`)            |

---

### **Data**

| Path                          | Type      | Description                                                  |
|-------------------------------|-----------|--------------------------------------------------------------|
| `data[].studyKey`             | String    | Unique study key for the given study                          |
| `data[].recordRevisionId`     | Number    | Unique system identifier for the record revision              |
| `data[].recordId`             | Number    | Unique system identifier for the related record               |
| `data[].recordOid`            | String    | Client-assigned record OID                                    |
| `data[].recordRevision`       | Number    | Record revision number                                        |
| `data[].dataRevision`         | Number    | Data revision number                                          |
| `data[].recordStatus`         | String    | User-defined record status                                    |
| `data[].subjectId`            | Number    | Mednet Subject ID                                             |
| `data[].subjectOid`           | String    | Client-assigned subject OID                                   |
| `data[].subjectKey`           | String    | Protocol-assigned subject identifier                          |
| `data[].siteId`               | Number    | Unique system identifier for the related site                 |
| `data[].formKey`              | String    | Form key                                                      |
| `data[].intervalId`           | Number    | Unique system identifier for the interval                     |
| `data[].role`                 | String    | Role of the user who saved the record revision                |
| `data[].user`                 | String    | Username of the user who saved the record revision            |
| `data[].reasonForChange`      | String    | Reason for the change made in the record revision             |
| `data[].deleted`              | Boolean   | Indicates whether the record was deleted                      |
| `data[].dateCreated`          | String    | Date when the record revision was created                     |

---

## Example Usage

### **Requesting Record Revisions for a Study**

To retrieve record revisions for a specific subject:

```http
GET /api/v1/edc/studies/PHARMADEMO/recordRevisions?page=0&size=25&sort=recordRevisionId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Record Revisions

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                          | Description                                                    |
|----------------------------------|----------------------------------------------------------------|
| `subjectKey==001-003`           | Returns record revisions for subject key `001-003`             |
| `recordStatus==Record Complete` | Returns revisions where the record status is "Record Complete" |
| `user==jdoe`                    | Returns record revisions made by user `jdoe`                   |
| `reasonForChange==Data entry error` | Returns revisions marked with the reason "Data entry error" |
| `deleted==true`                 | Returns deleted record revisions                               |
| `dateCreated>2024-01-01T00:00:00Z` | Returns revisions created after January 1, 2024             |

---

## Notes

- **Record Revisions Lifecycle:**
  - A new revision is created every time a record is modified or progresses to a new status.

- **Reason for Change:**
  - It's crucial to capture a meaningful `reasonForChange` when editing a record to maintain data integrity.

- **Deleted Records:**
  - Records marked as `deleted: true` can be filtered out or included as needed.

---
