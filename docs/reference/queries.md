# Queries Endpoint Documentation

## Overview

The **Queries Endpoint** allows users to fetch the set of **queries** for a given `StudyKey`. A **query** represents dialogue or questions related to specific eCRF responses or other aspects of study conduct. Queries may be **user-initiated** or **automatically generated** based on study protocol criteria.

---

## Accessing the Index

To retrieve queries, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/queries?page=0&size=25&sort=annotationId%2CASC&filter=variable%3D%3Daeterm HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                            |
|-------------|----------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of queries |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/queries
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `annotationId,asc`. |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/queries",
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
        "property": "annotationId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "subjectId": 1,
      "subjectOid": "OID-1",
      "annotationType": "subject",
      "annotationId": 1,
      "type": null,
      "description": "Monitor Query",
      "recordId": 123,
      "variable": "aeterm",
      "subjectKey": "123-005",
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20",
      "queryComments": [
        {
          "sequence": 1,
          "annotationStatus": "Monitor Query Open",
          "user": "john",
          "comment": "Added comment to study",
          "closed": false,
          "date": "2024-11-04 16:03:19"
        }
      ]
    }
  ]
}
```

---

## Response Fields

### **Metadata**

| Path                  | Type    | Description                                     |
|-----------------------|---------|-------------------------------------------------|
| `metadata.status`     | String  | HTTP status                                     |
| `metadata.method`     | String  | HTTP method used                                |
| `metadata.path`       | String  | Requested URI path                              |
| `metadata.timestamp`  | String  | Timestamp when the response was generated       |
| `metadata.error`      | Object  | Error details, if any                           |

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

| Path                                     | Type      | Description                                                   |
|------------------------------------------|-----------|---------------------------------------------------------------|
| `data[].studyKey`                        | String    | Unique study key                                              |
| `data[].subjectId`                       | Number    | Mednet Subject ID                                             |
| `data[].subjectOid`                      | String    | Client-assigned subject OID                                   |
| `data[].annotationType`                  | String    | User-defined identifier for Query Type                        |
| `data[].annotationId`                    | Number    | Unique system identifier for the Query Instance               |
| `data[].type`                            | Null      | System text identifier for query type/location (`subject`, `record`, `question`) |
| `data[].description`                     | String    | Query description                                             |
| `data[].subjectKey`                      | String    | Protocol-assigned subject identifier                          |
| `data[].recordId`                        | Number    | Unique system identifier for Record                           |
| `data[].variable`                        | String    | User-defined field identifier                                 |
| `data[].dateCreated`                     | String    | Date when the query was created                               |
| `data[].dateModified`                    | String    | Date when the query was modified                              |
| `data[].queryComments[].sequence`        | Number    | Query comment sequence                                        |
| `data[].queryComments[].user`            | String    | User performing the query action                              |
| `data[].queryComments[].annotationStatus`| String    | User-defined query status                                     |
| `data[].queryComments[].comment`         | String    | User comment applied during query action                      |
| `data[].queryComments[].closed`          | Boolean   | Indicates if the query was closed                             |
| `data[].queryComments[].date`            | String    | Date of the query comment                                     |

---

## Example Usage

### **Requesting Queries for a Study**

To retrieve queries from a study using a specific filter:

```http
GET /api/v1/edc/studies/PHARMADEMO/queries?page=0&size=25&sort=annotationId%2CASC&filter=variable%3D%3Daeterm HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Queries

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                          | Description                                                   |
|----------------------------------|---------------------------------------------------------------|
| `variable==aeterm`              | Returns queries for the field `aeterm`                        |
| `annotationType==subject`       | Returns all subject-level queries                             |
| `description==Monitor Query`    | Returns queries with the description "Monitor Query"          |
| `queryComments.user==john`      | Returns queries with comments made by user "john"             |
| `queryComments.closed==false`   | Returns queries that are still open                           |
| `dateCreated>2024-01-01T00:00:00Z` | Returns queries created after January 1, 2024              |

---

## Notes

- **Query Comments:**
  - Queries can have multiple comments, each with its own status, user, and timestamp.

- **Query Status:**
  - Statuses like "Monitor Query Open" help track the lifecycle of a query.

- **Open vs. Closed Queries:**
  - The `closed` boolean in `queryComments` indicates if a query is still open or has been resolved.

- **System-Generated Queries:**
  - Queries can be user-initiated or automatically generated based on study protocols.

---
