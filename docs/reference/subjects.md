# Subjects Endpoint Documentation

## Overview

The **Subjects Endpoint** allows users to fetch the set of **subjects** for a given `StudyKey`. A **subject** represents a single participant in a study and is related to **records** (one-to-many) and **sites** (each subject belongs to a site).

---

## Accessing the Index

To retrieve subjects, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/subjects?page=0&size=25&sort=subjectId%2CASC&filter=subjectId%3D%3D370 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                   |
|-------------|-----------------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of subjects    |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/subjects
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `subjectId,asc`.    |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/subjects",
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
        "property": "subjectId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "subjectId": 1,
      "subjectOid": "OID-1",
      "subjectKey": "01-001",
      "subjectStatus": "Enrolled",
      "siteId": 128,
      "siteName": "Chicago Hope Hospital",
      "deleted": false,
      "enrollmentStartDate": "2024-11-04 16:03:19",
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20",
      "keywords": [
        {
          "keywordName": "Data Entry Error",
          "keywordKey": "DEE",
          "keywordId": 15362,
          "dateAdded": "2024-11-04 16:03:19"
        }
      ]
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

| Path                            | Type      | Description                                                  |
|---------------------------------|-----------|--------------------------------------------------------------|
| `data[].studyKey`               | String    | Unique study key for the given study                          |
| `data[].subjectId`              | Number    | Mednet Subject ID                                             |
| `data[].subjectOid`             | String    | Client-assigned subject OID                                   |
| `data[].subjectKey`             | String    | Protocol-assigned subject identifier                          |
| `data[].subjectStatus`          | String    | Current status of the subject (e.g., Enrolled)                |
| `data[].siteId`                 | Number    | Mednet Site ID                                                |
| `data[].siteName`               | String    | Name of the site                                              |
| `data[].enrollmentStartDate`    | String    | Date when the subject enrollment started                      |
| `data[].deleted`                | Boolean   | Indicates whether the subject was deleted                     |
| `data[].dateCreated`            | String    | Date when the subject record was created                      |
| `data[].dateModified`           | String    | Last modification date of the subject record                  |
| `data[].keywords`               | Array     | List of keywords associated with the subject                  |
| `data[].keywords[].keywordName` | String    | Name of the keyword                                           |
| `data[].keywords[].keywordKey`  | String    | Unique key for the keyword                                    |
| `data[].keywords[].keywordId`   | Number    | Unique ID for the keyword                                     |
| `data[].keywords[].dateAdded`   | String    | Date when the keyword was added                               |

---

## Example Usage

### **Requesting Subjects for a Study**

To retrieve subjects for a specific study with a filter on `subjectId`:

```http
GET /api/v1/edc/studies/PHARMADEMO/subjects?page=0&size=25&sort=subjectId%2CASC&filter=subjectId%3D%3D370 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Subjects

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                                | Description                                                     |
|---------------------------------------|-----------------------------------------------------------------|
| `subjectId==370`                     | Returns the subject with `subjectId` equal to `370`             |
| `subjectStatus==Enrolled`            | Returns subjects with status `Enrolled`                         |
| `siteName==Chicago Hope Hospital`    | Returns subjects enrolled at "Chicago Hope Hospital"            |
| `deleted==false`                     | Returns active subjects (not deleted)                           |
| `enrollmentStartDate>2024-01-01T00:00:00Z` | Returns subjects enrolled after January 1, 2024          |

---

## Notes

- **Subject and Site Relationship:**
  - Each **subject** belongs to a specific **site** and has a unique identifier.

- **Enrollment Status:**
  - The `subjectStatus` field tracks the current enrollment status (e.g., Enrolled, Withdrawn).

- **Deleted Records:**
  - Subjects marked as `deleted: true` can be filtered out or included as needed.

- **Keywords:**
  - Subjects can have associated keywords for categorization or flagging specific data points.
