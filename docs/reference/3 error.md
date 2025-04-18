# Error Handling

## Overview

When an error occurs during a service call, detailed error information is returned under the `metadata` section of the response. This includes an associated error message to help diagnose and resolve issues. Common causes of errors include improperly formed requests, missing required parameters, or unauthorized access.

The error details can help identify the specific attribute that caused the failure, making it easier to debug and correct the issue.

---

## Error Response Structure

When an error is raised, the API returns a structured JSON response similar to the example below.

### Example Error Response

```json
{
  "metadata": {
    "status": "BAD_REQUEST",
    "path": "/api/v1/edc/studies",
    "timestamp": "2018-10-18 05:46:29",
    "error": {
      "code": "1000",
      "description": "Field raised validation errors",
      "field": {
        "attribute": "page",
        "value": "XX"
      }
    }
  }
}
```

---

## Error Response Fields

The following table describes the fields in the error response:

| Path                      | Type    | Description                                                          |
|---------------------------|---------|----------------------------------------------------------------------|
| `metadata.status`         | String  | HTTP status indicating the type of error (e.g., `BAD_REQUEST`)       |
| `metadata.path`           | String  | The API endpoint path that triggered the error                       |
| `metadata.timestamp`      | String  | Timestamp indicating when the error occurred                         |
| `metadata.error.code`     | String  | Error code representing the specific error type                      |
| `metadata.error.description` | String | Description providing details about the error                        |
| `metadata.error.field.attribute` | String | The request attribute that caused the error                     |
| `metadata.error.field.value` | String | The invalid value provided for the problematic attribute         |

---

## Error Codes

The following error codes may be returned by the API:

| Error Code | Description                                                           |
|------------|-----------------------------------------------------------------------|
| **1000**   | Validation error. The request contains an invalid value.              |
| **9000**   | Unknown error. Please contact Mednet support for assistance.          |
| **9001**   | Unauthorized error. Insufficient permissions to retrieve the data.    |

---

## Example Scenarios

### **1. Validation Error (`1000`)**

- **Scenario:** A required query parameter is provided with an invalid value.
- **Example Request:**

  ```http
  GET /api/v1/edc/studies?page=XX HTTP/1.1
  Content-Type: application/json
  ```

- **Example Error Response:**

  ```json
  {
    "metadata": {
      "status": "BAD_REQUEST",
      "path": "/api/v1/edc/studies",
      "timestamp": "2018-10-18 05:46:29",
      "error": {
        "code": "1000",
        "description": "Field raised validation errors",
        "field": {
          "attribute": "page",
          "value": "XX"
        }
      }
    }
  }
  ```

### **2. Unauthorized Error (`9001`)**

- **Scenario:** A request is made without proper authentication headers.
- **Example Response:**

  ```json
  {
    "metadata": {
      "status": "UNAUTHORIZED",
      "path": "/api/v1/edc/studies",
      "timestamp": "2024-11-04 16:03:19",
      "error": {
        "code": "9001",
        "description": "Unauthorized error. Insufficient permission to retrieve data."
      }
    }
  }
  ```

### **3. Unknown Error (`9000`)**

- **Scenario:** An unexpected server-side error occurs.
- **Example Response:**

  ```json
  {
    "metadata": {
      "status": "INTERNAL_SERVER_ERROR",
      "path": "/api/v1/edc/studies",
      "timestamp": "2024-11-04 16:03:19",
      "error": {
        "code": "9000",
        "description": "Unknown error. Please contact Mednet support for assistance."
      }
    }
  }
  ```

---

## Best Practices for Error Handling

1. **Validate Inputs:**
   Always validate request parameters before sending them to the API to minimize validation errors.

2. **Check for Required Fields:**
   Ensure all mandatory fields are included in your API requests.

3. **Handle HTTP Status Codes:**
   Implement robust error handling in your client to manage different HTTP status codes (`400`, `401`, `500`, etc.).

4. **Use Error Details for Debugging:**
   Utilize the `error` object in the response to pinpoint and fix issues.

---
