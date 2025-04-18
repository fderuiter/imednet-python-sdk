<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\todo\06_error_handling_and_exceptions.md -->
# Task 6: Error Handling and Exceptions

- [ ] Define a custom exception hierarchy in `imednet_sdk/exceptions.py`:
  - `ImednetSdkException` (base exception)
  - `ApiError(ImednetSdkException)` (for general API errors, e.g., 5xx)
  - `AuthenticationError(ImednetSdkException)` (for 401 Unauthorized)
  - `AuthorizationError(ImednetSdkException)` (for 403 Forbidden, e.g., invalid studyKey)
  - `BadRequestError(ImednetSdkException)` (for 400 Bad Request, general)
  - `ValidationError(BadRequestError)` (specifically for validation errors, code 1000)
  - `NotFoundError(ImednetSdkException)` (for 404 Not Found)
  - `RateLimitError(ImednetSdkException)` (for 429 Too Many Requests)
- [ ] In the `BaseClient`'s request handling logic, check the HTTP status code of the response.
- [ ] If the status code indicates an error (>= 400), attempt to parse the JSON response body to extract the `metadata.error` details.
- [ ] Map HTTP status codes and `metadata.error.code` to the custom exceptions:
  - `400 BAD_REQUEST`:
    - If `metadata.error.code == "1000"`: Raise `ValidationError`, including `description`, `attribute`, and `value` from the error payload.
    - Otherwise: Raise `BadRequestError`, including the description if available.
  - `401 UNAUTHORIZED`:
    - If `metadata.error.code == "9001"`: Raise `AuthenticationError` (likely invalid/missing API/Security keys).
    - Otherwise: Raise `AuthenticationError` with available details.
  - `403 FORBIDDEN`: Raise `AuthorizationError` (e.g., invalid `studyKey` access).
  - `404 NOT_FOUND`: Raise `NotFoundError`.
  - `429 TOO_MANY_REQUESTS`: Raise `RateLimitError`.
  - `500 INTERNAL_SERVER_ERROR`:
    - If `metadata.error.code == "9000"`: Raise `ApiError` (Unknown Error).
    - Otherwise: Raise `ApiError` with status code.
  - Other `4xx`/`5xx`: Raise a generic `ApiError` with the status code and response text.
    (Reference: `docs/reference/1 common.md` Status Codes and `docs/reference/3 error.md` Error Codes)
- [ ] Ensure exceptions store relevant context: HTTP status code, API error code, description, field details (if applicable), request path, and timestamp.
- [ ] Implement retry logic (in `BaseClient` or via a library like `tenacity`) for potentially transient errors (e.g., `RateLimitError`, `ApiError` for 5xx status codes) on idempotent requests (like GET).
