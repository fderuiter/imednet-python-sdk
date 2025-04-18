# Records Endpoint Documentation

## Overview

The **Records Endpoint** allows users to fetch or add records for a given `StudyKey`. A **record** represents a single instance of an **electronic case report form (eCRF)** and contains responses to each question on the eCRF.

---

## Accessing the Index

- **GET** request — Retrieve existing records.  
- **POST** request — Add new records to the iMednet database.

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                          |
|-------------|--------------------------------------|
| `studyKey`  | StudyKey to retrieve list of records |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/records
```

---

## GET Requests

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/records?page=0&size=25&sort=recordId%2CASC&filter=recordId%3D%3D5510&recordDataFilter=aeterm%3D%3DBronchitis HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

### Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter           | Description                                                                                                                                |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `page`              | Index page to return. Default is `0`.                                                                                                      |
| `size`              | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                       |
| `sort`              | Property to sort by. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default: `recordId,asc`. |
| `filter`            | Optional filter criteria. Must follow correct syntax. Refer to the **Common filter** section for details.                                  |
| `recordDataFilter`  | Optional filter for record data. Refer to the **Common record data filter** section for details.                                           |

---

### GET Response Body

#### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/records",
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
      "intervalId": 99,
      "formId": 10202,
      "formKey": "AE",
      "siteId": 128,
      "recordId": 1,
      "recordOid": "REC-1",
      "recordType": "SUBJECT",
      "recordStatus": "Record Incomplete",
      "deleted": false,
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20",
      "subjectId": 326,
      "subjectOid": "OID-1",
      "subjectKey": "123-456",
      "visitId": 1,
      "parentRecordId": 34,
      "keywords": [
        {
          "keywordName": "Data Entry Error",
          "keywordKey": "DEE",
          "keywordId": 15362,
          "dateAdded": "2024-11-04 16:03:19"
        }
      ],
      "recordData": {
        "dateCreated": "2018-10-18 06:21:46",
        "unvnum": "1",
        "dateModified": "2018-11-18 07:11:16",
        "aeser": "",
        "aeterm": "Bronchitis"
      }
    }
  ]
}
```

---

### GET Response Fields

#### Metadata

| Path                  | Type    | Description                                     |
|-----------------------|---------|-------------------------------------------------|
| `metadata.status`     | String  | HTTP status                                     |
| `metadata.method`     | String  | HTTP method used                                |
| `metadata.path`       | String  | Requested URI path                              |
| `metadata.timestamp`  | String  | Timestamp when the response was generated       |
| `metadata.error`      | Object  | Error details, if any                           |

---

#### Pagination

| Path                        | Type    | Description                                    |
|-----------------------------|---------|------------------------------------------------|
| `pagination.currentPage`    | Number  | Current page index                             |
| `pagination.size`           | Number  | Number of items per page                       |
| `pagination.totalPages`     | Number  | Total number of pages                          |
| `pagination.totalElements`  | Number  | Total number of elements                       |
| `pagination.sort[].property`| String  | Property used for sorting                      |
| `pagination.sort[].direction`| String | Sorting direction (`ASC` or `DESC`)            |

---

#### Data

| Path                        | Type      | Description                                           |
|-----------------------------|-----------|-------------------------------------------------------|
| `data[].studyKey`           | String    | Unique study key                                      |
| `data[].intervalId`         | Number    | Unique ID for the interval                            |
| `data[].formId`             | Number    | Form ID                                               |
| `data[].formKey`            | String    | Form key                                              |
| `data[].siteId`             | Number    | Unique site ID                                        |
| `data[].recordId`           | Number    | Unique system ID for the record                       |
| `data[].recordOid`          | String    | Client-assigned record OID                            |
| `data[].recordType`         | String    | Type of record                                        |
| `data[].recordStatus`       | String    | User-defined record status                            |
| `data[].subjectId`          | Number    | Mednet Subject ID                                     |
| `data[].subjectOid`         | String    | Client-assigned subject OID                           |
| `data[].subjectKey`         | String    | Protocol-assigned subject identifier                  |
| `data[].visitId`            | Number    | Unique ID for the subject visit                       |
| `data[].parentRecordId`     | Number    | Parent record ID                                      |
| `data[].deleted`            | Boolean   | Record deleted flag                                   |
| `data[].dateCreated`        | String    | Record creation date                                  |
| `data[].dateModified`       | String    | Last modification date                                |
| `data[].keywords`           | Array     | List of keywords associated with the record           |
| `data[].recordData`         | Object    | Detailed record data                                  |

---

## POST Requests

To add new records, use a **POST** request with a valid request body.

### POST Request Example

```http
POST /api/v1/edc/studies/PHARMADEMO/records HTTP/1.1
x-email-notify: user@domain.com
Accept: application/json
Content-Type: application/json
Host: localhost:8080

[ { /* request body */ } ]
```

---

### POST Request Identifiers

| Identifier        | Description                                      |
|-------------------|--------------------------------------------------|
| **Form Identifiers**     |                                              |
| `formKey`         | User-defined form key                            |
| `formId`          | System-generated form ID                         |
| **Site Identifiers**     |                                              |
| `siteName`        | User-defined site name                           |
| `siteId`          | System-generated site ID                         |
| **Subject Identifiers**  |                                              |
| `subjectKey`      | Protocol-assigned subject identifier             |
| `subjectId`       | System-generated subject ID                      |
| `subjectOid`      | Client-assigned subject OID                      |
| **Interval Identifiers** |                                              |
| `intervalName`    | User-defined interval name                       |
| `intervalId`      | System-generated interval ID                     |
| **Record Identifiers**   |                                              |
| `recordId`        | System-generated record ID                       |
| `recordOid`       | Client-assigned record OID                       |

---

### Field Types for POST

| Path                         | Type    | Description                    |
|------------------------------|---------|--------------------------------|
| `[].formKey`                 | String  | Form key                       |
| `[].siteName`                | String  | Site name                      |
| `[].data`                    | Object  | Data for specific record        |
| `[].data.textField`          | String  | Text field                     |
| `[].data.dateField`          | String  | Date field                     |
| `[].data.numberField`        | Number  | Number field                   |
| `[].data.radioField`         | String  | Radio field                    |
| `[].data.dropdownField`      | String  | Dropdown field                 |
| `[].data.memoField`          | String  | Memo field                     |
| `[].data.checkboxField`      | Boolean | Checkbox field                 |

---

### Example Scenarios

#### **1. Register Subject**

```json
[
  {
    "formKey": "REG",
    "siteName": "Minneapolis",
    "data": {
      "textField": "Text value"
    }
  }
]
```

---

#### **2. Update a Scheduled Record**

```json
[
  {
    "formKey": "REG",
    "subjectKey": "651-042",
    "intervalName": "Registration",
    "data": {
      "textField": "Updated text"
    }
  }
]
```

---

#### **3. Create a New Record**

```json
[
  {
    "formKey": "REG",
    "subjectKey": "123-876",
    "data": {
      "textField": "New record data"
    }
  }
]
```

---

### POST Response Body

#### POST Example Response

```json
{
  "jobId": "9663fe34-eec7-460a-a820-097f1eb2875e",
  "batchId": "c3q191e4-f894-72cd-a753-b37283eh0866",
  "state": "created"
}
```

| Field       | Type    | Description                                                         |
|-------------|---------|---------------------------------------------------------------------|
| `jobId`     | String  | Unique identifier for the job                                       |
| `batchId`   | String  | Batch ID associated with the submitted records                      |
| `state`     | String  | Status of the job (e.g., `created`)                                 |

---
