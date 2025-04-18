# Task 2: Core HTTP Client Implementation

- Design `BaseClient` class wrapping `requests.Session`
- Implement generic request methods (GET, POST, PUT, DELETE)
- Centralize base URL and path construction
- Use default base URL (`/api/v1/edc`) per reference docs
- Set default headers on each request: `Accept: application/json`, `Content-Type: application/json`, `x-api-key`, `x-imn-security-key`
- Support query parameters: `page` (default 0), `size` (default 25, max 500), `sort`, `filter` for pagination and filtering
- Integrate retry logic (exponential backoff)
- Handle connection pooling and timeout settings
- Define interface for pluggable HTTP adapters
