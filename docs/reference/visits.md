# Visits Endpoint Documentation

## Overview

The **Visits Endpoint** allows users to fetch the set of **visits** for a given `StudyKey`. A **visit** represents a single instance of an interval for a subject within a study.

---

## Accessing the Index

To retrieve visits, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/visits?page=0&size=25&sort=visitId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                      |
|-------------|--------------------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of visits          |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/visits
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `visitId,asc`.    |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/visits",
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
        "property": "visitId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "visitId": 1,
      "studyKey": "PHARMADEMO",
      "intervalId": 13,
      "intervalName": "Day 15",
      "subjectId": 247,
      "subjectKey": "111-005",
      "startDate": "2024-11-04",
      "endDate": "2024-11-11",
      "dueDate": null,
      "visitDate": "2024-11-06",
      "visitDateForm": "Follow Up",
      "deleted": false,
      "visitDateQuestion": "AESEV",
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:19"
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
| `data[].visitId`                | Number    | Unique system identifier for the subject visit instance       |
| `data[].studyKey`               | String    | Unique study key for the given study                          |
| `data[].intervalId`             | Number    | Unique system identifier for the related interval             |
| `data[].intervalName`           | String    | User-defined identifier for the related interval              |
| `data[].subjectId`              | Number    | Mednet Subject ID                                             |
| `data[].subjectKey`             | String    | Protocol-assigned subject identifier                          |
| `data[].startDate`              | String    | Subject visit Start Date defined in interval visit window     |
| `data[].endDate`                | String    | Subject visit End Date defined in interval visit window       |
| `data[].dueDate`                | Null      | Subject visit Due Date defined in interval visit window       |
| `data[].visitDate`              | String    | Subject visit Actual Date defined in interval visit window    |
| `data[].visitDateForm`          | String    | Actual Date Form defined in interval visit window             |
| `data[].visitDateQuestion`      | String    | User-defined field identifier                                 |
| `data[].deleted`                | Boolean   | Subject visit deleted flag                                    |
| `data[].dateCreated`            | String    | Date when this visit was created                              |
| `data[].dateModified`           | String    | Date when this visit was last modified                        |

---

## Example Usage

### **Requesting Visits for a Study**

To retrieve visits for a specific study with a filter on `subjectKey`:

```http
GET /api/v1/edc/studies/PHARMADEMO/visits?page=0&size=25&sort=visitId%2CASC&filter=subjectKey%3D%3D270 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Visits

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                                  | Description                                                     |
|-----------------------------------------|-----------------------------------------------------------------|
| `subjectKey==270`                      | Returns visits for the subject with `subjectKey` equal to `270` |
| `intervalName==Day 15`                 | Returns visits for the interval named "Day 15"                  |
| `visitDate>=2024-11-01`                | Returns visits occurring on or after November 1, 2024           |
| `deleted==false`                       | Returns only active (non-deleted) visits                        |

---

## Notes

- **Visit and Interval Relationship:**  
  - Each **visit** is associated with a specific **interval** for a subject.

- **Date Fields:**  
  - The `startDate`, `endDate`, `dueDate`, and `visitDate` fields provide scheduling and actual visit information.

- **Deleted Visits:**  
  - Visits marked as `deleted: true` can be filtered out or included as needed.

- **Pagination:**  
  - Use the `page` and `size` parameters to control pagination and limit the number of visits returned.
