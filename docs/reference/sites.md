# Sites Endpoint Documentation

## Overview

The **Sites Endpoint** allows users to fetch the set of **sites** for a given `StudyKey`. A **site** represents a hospital, clinic, or other geographic entity where subjects participate in the study. Each site can have multiple associated subjects.

---

## Accessing the Index

To retrieve sites, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/sites?page=0&size=25&sort=siteId%2CASC&filter=siteId%3D%3D48 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                                  |
|-------------|--------------------------------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of sites for the specific study |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/sites
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `siteId,asc`.      |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/sites",
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
        "property": "siteId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "siteId": 1,
      "siteName": "Mock Site 1",
      "siteEnrollmentStatus": "Enrollment Open",
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20"
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
| `data[].siteId`               | Number    | Unique system identifier for the site                         |
| `data[].siteName`             | String    | Name of the site                                              |
| `data[].siteEnrollmentStatus` | String    | Current enrollment status of the site                         |
| `data[].dateCreated`          | String    | Date when the site record was created                         |
| `data[].dateModified`         | String    | Last modification date of the site record                     |

---

## Example Usage

### **Requesting Sites for a Study**

To retrieve sites for a specific study with a filter on `siteId`:

```http
GET /api/v1/edc/studies/PHARMADEMO/sites?page=0&size=25&sort=siteId%2CASC&filter=siteId%3D%3D48 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Sites

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                          | Description                                              |
|----------------------------------|----------------------------------------------------------|
| `siteId==48`                    | Returns the site with `siteId` equal to `48`            |
| `siteEnrollmentStatus==Enrollment Open` | Returns all sites with open enrollment          |
| `siteName==Mock Site 1`         | Returns the site named "Mock Site 1"                    |
| `dateCreated>2024-01-01T00:00:00Z` | Returns sites created after January 1, 2024        |

---

## Notes

- **Site and Subject Relationship:**
  - Each **site** can have one-to-many subjects enrolled in the study.

- **Enrollment Status:**
  - The `siteEnrollmentStatus` field indicates whether the site is actively enrolling subjects.

- **Filtering and Sorting:**
  - Sites can be filtered and sorted using multiple parameters to refine search results.

---
