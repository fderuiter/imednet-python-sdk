# Task 2: Core HTTP Client Implementation

- [ ] Design a `BaseClient` class, potentially using `httpx` or `requests.Session` for features like connection pooling.
- [ ] Implement generic request methods (`_get`, `_post`, `_put`, `_delete`) within `BaseClient`.
- [ ] Centralize base URL construction. The default base URL is `https://edc.prod.imednetapi.com` (from `docs/reference/1 common.md`).
- [ ] Ensure all requests automatically include the required headers:
  - `Accept: application/json`
  - `Content-Type: application/json`
  - `x-api-key: <your_api_key>`
  - `x-imn-security-key: <your_security_key>`
    (Reference: `docs/reference/1 common.md` and `docs/reference/2 header.md`)
- [ ] Implement support for standard query parameters used across endpoints:
  - `page`: Page index (default: 0)
  - `size`: Items per page (default: 25, max: 500)
  - `sort`: Sorting criteria (e.g., `property,asc` or `property,desc`)
  - `filter`: Resource-specific filtering (syntax varies, see `docs/reference/1 common.md`)
  - `recordDataFilter`: Specific filter for `recordData` field in Records endpoint (see `docs/reference/1 common.md` and `docs/reference/records.md`)
- [ ] Integrate configurable retry logic (e.g., using `urllib3.util.retry` or `tenacity`) for transient network errors or specific HTTP status codes (like 429 Too Many Requests, 5xx Server Errors).
- [ ] Implement configurable timeout settings for requests.
- [ ] (Optional) Define an interface for pluggable HTTP adapters if advanced customization is needed (e.g., different HTTP libraries).
