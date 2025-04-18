# Users Endpoint Documentation

## Overview

The **Users Endpoint** allows users to fetch the set of **users** for a given `StudyKey`. This endpoint provides detailed information about users and their roles within the study.

---

## Accessing the Index

To retrieve users, use a **GET** request.

### Request Example

```http
GET /api/v1/edc/studies/MOCK-STUDY/users?page=0&size=25&includeInactive=false&sort=login%2CASC HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Path Parameters

Path parameters are **required**.

| Parameter   | Description                                      |
|-------------|--------------------------------------------------|
| `studyKey`  | StudyKey to retrieve the list of users          |

**Endpoint Structure:**

```http
/api/v1/edc/studies/{studyKey}/users
```

---

## Request Parameters

Request parameters are **optional**. Defaults will be used if not specified.

| Parameter        | Description                                                                                                                                                           |
|------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page`           | Index page to return. Default is `0`.                                                                                                                                 |
| `size`           | Number of items per page. Default is `25`. Maximum allowed is `500`.                                                                                                  |
| `sort`           | Property to sort the result set. Format: `property,asc` or `property,desc`. To sort by multiple properties, use multiple `sort` params. Default is `login,asc`.      |
| `includeInactive`| Boolean flag indicating whether to include inactive users. Default is `false`.                                                                                       |

---

## Response Body

### Example Response

```json
{
  "metadata": {
    "status": "OK",
    "method": "GET",
    "path": "/api/v1/edc/studies/MOCK-STUDY/users",
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
        "property": "login",
        "direction": "ASC"
      }
    ]
  },
  "data": [
    {
      "userId": "ed4cb749-9e65-40d3-a15d-cc83d4e68ded",
      "login": "wsmith1",
      "firstName": "William",
      "lastName": "Smith",
      "email": "wsmith@mednet.com",
      "userActiveInStudy": true,
      "roles": [
        {
          "dateCreated": [2024, 11, 4, 16, 3, 18, 487000000],
          "dateModified": [2024, 11, 4, 16, 3, 18, 487000000],
          "roleId": "bb5bae9d-5869-41b4-ae29-6d28f6200c85",
          "communityId": 1,
          "name": "Role name 1",
          "description": "Role description 1",
          "level": 1,
          "type": "Role type 1",
          "inactive": false
        },
        {
          "dateCreated": [2024, 11, 4, 16, 3, 18, 487000000],
          "dateModified": [2024, 11, 4, 16, 3, 18, 487000000],
          "roleId": "bb5bae9d-5869-41b4-ae29-6d28f6200c85",
          "communityId": 2,
          "name": "Role name 2",
          "description": "Role description 2",
          "level": 2,
          "type": "Role type 2",
          "inactive": false
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

#### User Fields

| Path                      | Type      | Description                                                  |
|---------------------------|-----------|--------------------------------------------------------------|
| `data[].userId`           | String    | Unique User ID                                               |
| `data[].login`            | String    | User login name                                              |
| `data[].firstName`        | String    | User's first name                                            |
| `data[].lastName`         | String    | User's last name                                             |
| `data[].email`            | String    | User's email address                                         |
| `data[].userActiveInStudy`| Boolean   | Indicates if the user is active in the study                 |

#### Role Fields

| Path                              | Type      | Description                                                  |
|-----------------------------------|-----------|--------------------------------------------------------------|
| `data[].roles[].dateCreated`      | Array     | Date when the role was created (format: `[YYYY, MM, DD, HH, MM, SS, NNNNNNNNN]`) |
| `data[].roles[].dateModified`     | Array     | Date when the role was last modified                         |
| `data[].roles[].roleId`           | String    | Unique Role ID                                               |
| `data[].roles[].communityId`      | Number    | Community ID associated with the role                        |
| `data[].roles[].name`             | String    | Name of the role                                             |
| `data[].roles[].description`      | String    | Description of the role                                      |
| `data[].roles[].level`            | Number    | Role level                                                   |
| `data[].roles[].type`             | String    | Type of role                                                 |
| `data[].roles[].inactive`         | Boolean   | Indicates if the role is inactive                            |

---

## Example Usage

### **Requesting Users for a Study**

To retrieve users for a specific study, excluding inactive users:

```http
GET /api/v1/edc/studies/MOCK-STUDY/users?page=0&size=25&includeInactive=false&sort=login%2CASC HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

To include inactive users:

```http
GET /api/v1/edc/studies/MOCK-STUDY/users?page=0&size=25&includeInactive=true&sort=login%2CASC HTTP/1.1
Content-Type: application/json
Host: localhost:8080
```

---

## Filtering and Sorting Users

The **sort** parameter allows sorting by user login or any other valid field. Use `asc` or `desc` for ascending or descending order.

### **Example Sort:**

| Sort Parameter                  | Description                                       |
|---------------------------------|---------------------------------------------------|
| `sort=login,asc`                | Sorts users by login in ascending order           |
| `sort=lastName,desc`            | Sorts users by last name in descending order      |

---

## Notes

- **Inactive Users:**
  - Set `includeInactive=true` to include inactive users in the response.

- **Roles:**
  - Each user may have multiple roles within the study, each with detailed attributes like role name, description, and community association.

- **Pagination:**
  - Use the `page` and `size` parameters to control pagination and limit the number of users returned.
