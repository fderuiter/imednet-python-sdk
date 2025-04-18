# Intervals Endpoint Documentation

## Overview

The **Intervals Endpoint** allows users to fetch the set of **intervals** for a given `StudyKey`. An **interval** is a design resource representing a set of **forms** that must be completed for each subject in a study. Intervals are linked to **visits**, where each visit is a single instance of an interval for a given subject.

---

## Accessing the Index

To retrieve intervals, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/intervals?page=0&size=25&sort=intervalId%2CASC&filter=intervalId%3D%3D161 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                          |
|-------------|--------------------------------------|
| `studyKey`  | StudyKey to retrieve list of intervals |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/intervals
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `intervalId,asc`.  |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/intervals",
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
        "property": "intervalId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "intervalId": 1,
      "intervalName": "Day 1",
      "intervalDescription": "Day 1",
      "intervalSequence": 110,
      "intervalGroupId": 10,
      "intervalGroupName": "ePRO",
      "disabled": true,
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20",
      "timeline": "Start Date End Date",
      "definedUsingInterval": "Baseline",
      "windowCalculationForm": "Procedure",
      "windowCalculationDate": "PROCDT",
      "actualDateForm": "Follow Up",
      "actualDate": "FUDT",
      "dueDateWillBeIn": 30,
      "negativeSlack": 7,
      "positiveSlack": 7,
      "eproGracePeriod": 2,
      "forms": [
        {
          "formId": 123,
          "formKey": "MY-FORM-KEY",
          "formName": "myFormName"
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

| Path                           | Type     | Description                                                        |
|--------------------------------|----------|--------------------------------------------------------------------|
| `data[].studyKey`              | String   | Unique study key                                                   |
| `data[].intervalId`            | Number   | Unique system identifier for the interval                          |
| `data[].intervalName`          | String   | User-defined interval/visit name                                   |
| `data[].intervalDescription`   | String   | User-defined interval/visit description                            |
| `data[].intervalSequence`      | Number   | User-defined sequence of the interval                              |
| `data[].intervalGroupId`       | Number   | User-defined interval group ID                                     |
| `data[].intervalGroupName`     | String   | User-defined interval group name                                   |
| `data[].timeline`              | String   | Type of Interval Visit Window (`None`, `Due Date`, `Start - End Date`, or `Actual Date`) |
| `data[].definedUsingInterval`  | String   | Baseline interval used for date calculations                       |
| `data[].windowCalculationForm` | String   | Baseline form used for date calculations                           |
| `data[].windowCalculationDate` | String   | Baseline field used for date calculations                          |
| `data[].actualDateForm`        | String   | Actual date form for a specific interval                           |
| `data[].actualDate`            | String   | Actual date field for a specific interval                          |
| `data[].dueDateWillBeIn`       | Number   | Number of days from the baseline date the interval is due          |
| `data[].negativeSlack`         | Number   | Allowed number of negative days from the due date                  |
| `data[].positiveSlack`         | Number   | Allowed number of positive days from the due date                  |
| `data[].eproGracePeriod`       | Number   | Allowed number of positive days for ePRO from the due date         |
| `data[].forms[].formId`        | Number   | Form ID                                                            |
| `data[].forms[].formKey`       | String   | Form Key                                                           |
| `data[].forms[].formName`      | String   | Form Name                                                          |
| `data[].disabled`              | Boolean  | Indicates if the interval is soft-deleted                          |
| `data[].dateCreated`           | String   | Date when the interval was created                                 |
| `data[].dateModified`          | String   | Last modification date of the interval                             |

---

## Example Usage

### **Requesting Intervals for a Study**

To retrieve intervals from a study using a specific filter:

```http
GET /api/v1/edc/studies/PHARMADEMO/intervals?page=0&size=25&sort=intervalId%2CASC&filter=intervalId%3D%3D161 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Intervals

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                           | Description                                              |
|-----------------------------------|----------------------------------------------------------|
| `intervalId==161`                | Returns the interval with `intervalId` equal to `161`    |
| `intervalGroupName==ePRO`        | Returns all intervals in the `ePRO` group                |
| `intervalName==Day 1`            | Returns intervals named "Day 1"                          |
| `disabled==false`                | Returns all active (non-disabled) intervals              |
| `dateCreated>2024-01-01T00:00:00Z`| Returns intervals created after January 1, 2024        |

---

## Notes

- **Interval and Visits:**  
  - Each **interval** represents a set of forms for a specific phase of a study, while a **visit** is a specific instance of an interval for a subject.

- **Window Calculations:**  
  - Date calculations for due dates and visit windows are based on baseline forms and fields defined in the interval.

- **Soft Deleted Intervals:**  
  - Intervals marked as `disabled: true` are soft deleted and can be filtered out using `disabled==false`.
