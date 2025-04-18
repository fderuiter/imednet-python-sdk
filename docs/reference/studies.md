# Studies Endpoint Documentation

## Overview

The **Studies Endpoint** allows users to fetch the set of **studies** accessible through a valid **API Key**. Only studies that the API key is authorized to view will be returned in the response.

---

## Accessing the Index

To retrieve studies, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies?page=0&size=25&sort=studyKey%2CASC&filter=studyKey%3D%3DPHARMADEMO HTTP/1.1
x-imn-security-key: my-security-key
x-api-key: my-api-token
Content-Type: application/json
Host: localhost:8080
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `studyKey,asc`.    |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Headers

The following headers must be included in the request:

| Header Name           | Description                                                                          |
|-----------------------|--------------------------------------------------------------------------------------|
| `x-api-key`           | Valid API key used for authentication.                                               |
| `x-imn-security-key`  | Valid security key for additional request authentication.                            |
| `Content-Type`        | Supported media type for request payload. Must be set to `application/json`.         |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies",
    "timestamp": "2024-11-04 16:03:18",
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
      "dateCreated": "2024-11-04 16:03:18",
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

| Path                          | Type      | Description                                                  |
|-------------------------------|-----------|--------------------------------------------------------------|
| `data[].sponsorKey`           | String    | Sponsor key that this study belongs to                        |
| `data[].studyKey`             | String    | Unique study key                                              |
| `data[].studyId`              | Number    | Mednet study ID                                               |
| `data[].studyName`            | String    | Study name                                                    |
| `data[].studyDescription`     | String    | Detailed description of the study                              |
| `data[].studyType`            | String    | Type of the study                                             |
| `data[].dateCreated`          | String    | Date when the study record was created                        |
| `data[].dateModified`         | String    | Last modification date of the study record                    |

---

## Example Usage

### **Requesting Studies**

To retrieve studies accessible by the provided API key:

```http
GET /api/v1/edc/studies?page=0&size=25&sort=studyKey%2CASC&filter=studyKey%3D%3DPHARMADEMO HTTP/1.1
x-imn-security-key: my-security-key
x-api-key: my-api-token
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Studies

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                                | Description                                                      |
|---------------------------------------|------------------------------------------------------------------|
| `studyKey==PHARMADEMO`               | Returns the study with `studyKey` equal to `PHARMADEMO`         |
| `sponsorKey==100`                    | Returns studies belonging to sponsor key `100`                   |
| `studyName==iMednet Pharma Demonstration Study` | Returns studies with the specified name             |
| `dateCreated>2024-01-01T00:00:00Z`   | Returns studies created after January 1, 2024                    |

---

## Notes

- **Authentication:**
  - Valid `x-api-key` and `x-imn-security-key` headers are required for authentication.

- **Pagination:**
  - Use the `page` and `size` parameters to control pagination and limit the number of studies returned.

- **Sorting and Filtering:**
  - Studies can be sorted and filtered using multiple parameters to refine search results.

- **Security:**
  - Ensure API keys and security tokens are kept confidential and not exposed publicly.

---
