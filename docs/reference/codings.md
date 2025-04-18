# Codings Endpoint Documentation

## Overview

The **Codings Endpoint** allows users to fetch the **coding activity** for a given `StudyKey`. Coding activity refers to the standardization of data entered into **iMednet** to specific drug or medical terms.

---

## Accessing the Index

To retrieve coding activity, send a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/codings?page=0&size=25&sort=recordId%2CASC&filter=dictionaryName%3DMedDRA HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter  | Description                              |
|------------|------------------------------------------|
| `studyKey` | The StudyKey to retrieve codings for    |

---

## Request Parameters

Request parameters are **optional**. Defaults are used unless specified.

| Parameter | Description                                                                                                                                                          |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`    | Index page to return. Default is `0`.                                                                                                                                |
| `size`    | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                 |
| `sort`    | Property to sort the result by. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` parameters. Default is `formId,asc`. |
| `filter`  | Filter criteria. Must follow correct syntax. Refer to the **Filtering** section for details.                                                                          |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/codings",
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
        "property": "recordId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "siteName": "Chicago Hope Hospital",
      "siteId": 128,
      "subjectId": 247,
      "subjectKey": "111-005",
      "formId": 1,
      "formName": "Adverse Event",
      "formKey": "AE",
      "revision": 2,
      "recordId": 1,
      "variable": "AETERM",
      "value": "Angina",
      "codingId": 1,
      "code": "Angina agranulocytic",
      "codedBy": "John Smith",
      "reason": "Typo fix",
      "dictionaryName": "MedDRA",
      "dictionaryVersion": "24.0",
      "dateCoded": "2024-11-04 16:03:19"
    }
  ]
}
```

---

## Response Fields

### **Metadata**

| Path                | Type   | Description                                       |
|---------------------|--------|---------------------------------------------------|
| `metadata.status`   | String | HTTP status                                       |
| `metadata.method`   | String | HTTP method used                                  |
| `metadata.path`     | String | Requested URI path                                |
| `metadata.timestamp`| String | Timestamp when the response was generated         |
| `metadata.error`    | Object | Error details, if any                             |

---

### **Pagination**

| Path                        | Type   | Description                                         |
|-----------------------------|--------|-----------------------------------------------------|
| `pagination.currentPage`    | Number | Current page index                                  |
| `pagination.size`           | Number | Number of items per page                            |
| `pagination.totalPages`     | Number | Total number of pages                               |
| `pagination.totalElements`  | Number | Total number of elements                            |
| `pagination.sort[].property`| String | Property used for sorting                           |
| `pagination.sort[].direction`| String | Sorting direction (`ASC` or `DESC`)                |

---

### **Data**

| Path                    | Type    | Description                                           |
|-------------------------|---------|-------------------------------------------------------|
| `data[].studyKey`       | String  | Unique Study Key                                      |
| `data[].siteName`       | String  | Name of the site                                      |
| `data[].siteId`         | Number  | Unique site ID                                        |
| `data[].subjectId`      | Number  | Mednet Subject ID                                     |
| `data[].subjectKey`     | String  | Protocol-assigned subject identifier                  |
| `data[].formId`         | Number  | Mednet Form ID                                        |
| `data[].formName`       | String  | Name of the eCRF                                      |
| `data[].formKey`        | String  | Form key                                              |
| `data[].revision`       | Number  | Number of modifications to the coding metadata        |
| `data[].recordId`       | Number  | Unique system identifier for the record               |
| `data[].variable`       | String  | Name of the variable on the eCRF                      |
| `data[].value`          | String  | Value entered                                         |
| `data[].codingId`       | Number  | Mednet Coding ID                                      |
| `data[].code`           | String  | Standardized code                                     |
| `data[].codedBy`        | String  | User who recorded the code                            |
| `data[].reason`         | String  | Reason for the coding                                 |
| `data[].dictionaryName` | String  | Name of the coding dictionary (e.g., MedDRA)          |
| `data[].dictionaryVersion`| String| Version of the coding dictionary                      |
| `data[].dateCoded`      | String  | Date when the code was added                          |

---

## Example Usage

### **Requesting Codings for a Study**

To retrieve codings from a study using the **MedDRA** dictionary, run:

```http
GET /api/v1/edc/studies/PHARMADEMO/codings?page=0&size=25&sort=recordId%2CASC&filter=dictionaryName%3DMedDRA HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Codings

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                         | Description                                                     |
|---------------------------------|-----------------------------------------------------------------|
| `dictionaryName==MedDRA`        | Returns codings from the MedDRA dictionary                      |
| `codedBy==John Smith`           | Returns codings recorded by John Smith                          |
| `dictionaryVersion>=24.0`       | Returns codings from dictionary version 24.0 or higher          |
| `siteName==Chicago Hope Hospital`| Returns codings from a specific site                           |
| `dateCoded>2024-01-01T00:00:00Z`| Returns codings added after January 1, 2024                     |
