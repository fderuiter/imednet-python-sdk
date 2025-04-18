# Task 6: Error Handling and Exceptions

- Define a custom exception hierarchy (e.g., `ApiError`, `AuthenticationError`, `ValidationError`)
- Map HTTP status codes to specific exceptions:
  - 400 BAD_REQUEST -> ValidationError (metadata.error.code == "1000")
  - 401 UNAUTHORIZED -> AuthenticationError (metadata.error.code == "9001")
  - 500 INTERNAL_SERVER_ERROR -> ApiError (metadata.error.code == "9000")
- Parse and surface API error payloads (message, code, details):
  - `metadata.error.code`, `metadata.error.description`
  - `metadata.error.field.attribute`, `metadata.error.field.value`
- Implement retry logic for idempotent operations on transient errors (retry on 500)
- Ensure exceptions include context (endpoint, parameters) for debugging
