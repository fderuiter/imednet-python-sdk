# Forms Endpoint Documentation

## Overview

The **Forms Endpoint** allows users to fetch the set of **forms** for a given `StudyKey`. A **form** is a design resource representing an **electronic clinical case report form (eCRF)**. Each form contains multiple questions and is linked to **records**, where each record represents a single instance of a form completed for a specific subject.

---

## Accessing the Index

To retrieve forms, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/PHARMADEMO/forms?page=0&size=25&sort=formId%2CASC&filter=formId%3D%3D10265 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                          |
|-------------|--------------------------------------|
| `studyKey`  | StudyKey to retrieve list of forms   |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/forms
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter   | Description                                                                                                                                                           |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`      | Index page to return. Default is `0`.                                                                                                                                 |
| `size`      | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`      | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `formId,asc`.      |
| `filter`    | Optional filter criteria. Must follow correct syntax. Refer to the **Filter** section for details.                                                                    |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/PHARMADEMO/forms",
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
        "property": "formId",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "studyKey": "PHARMADEMO",
      "formId": 1,
      "formKey": "FORM_1",
      "formName": "Mock Form 1",
      "formType": "Subject",
      "revision": 1,
      "embeddedLog": false,
      "enforceOwnership": false,
      "userAgreement": false,
      "subjectRecordReport": false,
      "unscheduledVisit": false,
      "otherForms": false,
      "eproForm": false,
      "allowCopy": true,
      "disabled": false,
      "dateCreated": "2024-11-04 16:03:19",
      "dateModified": "2024-11-04 16:03:20"
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
| `data[].formId`                | Number   | Mednet Form ID                                                     |
| `data[].formKey`               | String   | Form key                                                           |
| `data[].formName`              | String   | Name of the eCRF                                                   |
| `data[].formType`              | String   | eCRF Type (e.g., Subject, Site)                                    |
| `data[].revision`              | Number   | Number of modifications to the form metadata                       |
| `data[].embeddedLog`           | Boolean  | Embedded Log checkbox value on the form attributes                 |
| `data[].enforceOwnership`      | Boolean  | Enforce Ownership checkbox value on the form attributes            |
| `data[].userAgreement`         | Boolean  | User Agreement checkbox value on the form attributes               |
| `data[].subjectRecordReport`   | Boolean  | Subject Record Report checkbox value on the form attributes        |
| `data[].unscheduledVisit`      | Boolean  | Include in Unscheduled Visits checkbox value on the form attributes|
| `data[].otherForms`            | Boolean  | Include in Other Forms checkbox value on the form attributes       |
| `data[].eproForm`              | Boolean  | Is ePRO checkbox value on the form attributes                      |
| `data[].allowCopy`             | Boolean  | Allow Copy checkbox value on the form attributes                   |
| `data[].disabled`              | Boolean  | Form is soft delete status                                         |
| `data[].dateCreated`           | String   | Date when the form was created                                     |
| `data[].dateModified`          | String   | Last modification date of the form                                 |

---

## Example Usage

### **Requesting Forms for a Study**

To retrieve forms from a study using a specific filter:

```http
GET /api/v1/edc/studies/PHARMADEMO/forms?page=0&size=25&sort=formId%2CASC&filter=formId%3D%3D10265 HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering Forms

The **filter** parameter allows users to refine results. Filters must follow the correct syntax.

### **Example Filters:**

| Filter                         | Description                                             |
|---------------------------------|---------------------------------------------------------|
| `formId==10265`                | Returns the form with `formId` equal to `10265`         |
| `formType==Subject`            | Returns all forms of type `Subject`                     |
| `formName==Mock Form 1`        | Returns the form named "Mock Form 1"                    |
| `disabled==false`              | Returns all active (non-disabled) forms                 |
| `dateCreated>2024-01-01T00:00:00Z` | Returns forms created after January 1, 2024         |

---

## Notes

- **eCRF Types** can include different form categories, such as `Subject` or `Site`.
- The **Allow Copy** and **Enforce Ownership** flags help manage form behaviors within the system.
- **Soft Deleted Forms:** Forms marked as `disabled: true` are soft deleted and can be filtered out using `disabled==false`.

---
