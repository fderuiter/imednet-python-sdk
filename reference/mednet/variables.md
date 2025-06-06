# Variables Endpoint Documentation

## Overview

The **Variables Endpoint** allows you to fetch a set of variables for a given `StudyKey`. A variable represents a data point on an electronic clinical case report form (**eCRF**). Each eCRF contains multiple variables, and these variables are linked to records, where each record holds responses to each variable within the `recordData` property.

---

## Accessing the Index

To access the index, send a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/variables?page=0&size=25&sort=variableId%2CASC&filter=variableId%3D%3D10299 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter | Description                           |
|-----------|---------------------------------------|
| studyKey  | The StudyKey to retrieve variables   |

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not provided.

| Parameter | Description                                                                                                                                                            |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| page      | Index page to return. Default is `0`.                                                                                                                                 |
| size      | Number of items per page. Default is `25`. Max allowed is `500`.                                                                                                       |
| sort      | Property to sort the result by. Use format `property,asc` or `property,desc`. For multiple properties, use multiple `sort` params. Default is `formId,asc`.            |
| filter    | Filter criteria using the correct syntax. Refer to the **Filter** section for details.                                                                                 |

---

## Response Body

An example of a response payload:

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/variables",
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
        "property": "variableId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "variableId": 1,
      "variableType": "RADIO",
      "variableName": "Pain Level",
      "sequence": 1,
      "revision": 1,
      "disabled": false,
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20",
      "formId": 108727,
      "variableOid": "OID-1",
      "deleted": false,
      "formKey": "FORM_1",
      "formName": "Pre-procedure screening",
      "label": "Select patient pain level between 1 and 10",
      "blinded": false
    }
  ]
}
```

---

## Response Fields

### Metadata

| Path               | Type    | Description                                     |
|--------------------|---------|-------------------------------------------------|
| metadata.status    | String  | HTTP status                                     |
| metadata.method    | String  | HTTP method used                                |
| metadata.path      | String  | Requested URI path                              |
| metadata.timestamp | String  | Timestamp of response generation                |
| metadata.error     | Object  | Error details, if any                           |

### Pagination

| Path                      | Type    | Description                                              |
|---------------------------|---------|----------------------------------------------------------|
| pagination.currentPage    | Number  | Current page index                                       |
| pagination.size           | Number  | Number of items per page                                 |
| pagination.totalPages     | Number  | Total number of pages                                    |
| pagination.totalElements  | Number  | Total number of elements                                 |
| pagination.sort[].property| String  | Property used for sorting                                |
| pagination.sort[].direction| String | Direction of sorting (`ASC` or `DESC`)                   |

### Data

| Path                  | Type     | Description                                            |
|-----------------------|----------|--------------------------------------------------------|
| data[].studyKey       | String   | Unique Study Key                                       |
| data[].variableId     | Number   | Mednet Variable ID                                     |
| data[].variableType   | String   | Type of the variable (e.g., RADIO, TEXT)               |
| data[].variableName   | String   | Name of the variable on the eCRF                       |
| data[].sequence       | Number   | User-defined sequence of the variable                  |
| data[].revision       | Number   | Number of modifications to the form metadata           |
| data[].disabled       | Boolean  | Flag indicating if the variable is disabled            |
| data[].dateCreated    | String   | Creation date of the variable                          |
| data[].dateModified   | String   | Last modification date of the variable                 |
| data[].formId         | Number   | Mednet Form ID                                         |
| data[].variableOid    | String   | Client-assigned Variable OID                           |
| data[].deleted        | Boolean  | Flag indicating if the variable is deleted             |
| data[].formKey        | String   | Form key                                               |
| data[].formName       | String   | Name of the eCRF                                       |
| data[].label          | String   | User-defined field label                               |
| data[].blinded        | Boolean  | Flag indicating if the variable is blinded             |
