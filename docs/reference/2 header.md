# Header Reference

## Overview

Headers are **required** for all API endpoints to ensure proper authentication and content negotiation. Both **request** and **response** headers must follow the guidelines outlined below.

---

## Request Headers

The following headers must be included in all API requests:

| Header Name           | Description                                                                          |
|-----------------------|--------------------------------------------------------------------------------------|
| **`Accept`**          | Specifies the expected response media type. Must be set to `application/json`.       |
| **`x-api-key`**       | Valid API key used for authentication.                                               |
| **`x-imn-security-key`** | Valid security key for additional request authentication.                        |
| **`Content-Type`**    | Specifies the media type of the request payload. Must be set to `application/json`.  |

---

### Example Request with Headers

```http
GET /api/v1/edc/studies/PHARMADEMO/records HTTP/1.1
Host: localhost:8080
Accept: application/json
Content-Type: application/json
x-api-key: YOUR_API_KEY
x-imn-security-key: YOUR_SECURITY_KEY
```

---

## Response Headers

The API responses will include the following headers:

| Header Name           | Description                                                                   |
|-----------------------|-------------------------------------------------------------------------------|
| **`Content-Type`**    | Specifies the content type of the response payload. Will be `application/json`. |

---

### Example Response with Headers

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "metadata": {
    "status": "OK",
    "timestamp": "2024-11-04T16:03:19Z"
  },
  "data": []
}
```

---

## Important Notes

1. **Authentication:**  
   - Both `x-api-key` and `x-imn-security-key` are mandatory for authentication.
   - Ensure keys are stored securely and not exposed publicly.

2. **Content Negotiation:**  
   - The `Accept` and `Content-Type` headers must be explicitly set to `application/json` for both requests and responses.

3. **Error Handling:**  
   - If headers are missing or invalid, the API will return an appropriate error with status codes like `400 Bad Request` or `401 Unauthorized`.

---
