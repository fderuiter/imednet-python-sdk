# Task 06: Error Handling and Exceptions

**Objective:** Define and implement a robust error handling mechanism using custom exceptions mapped from API responses, including retry logic for transient errors.

**Definition of Done:**

* A custom exception hierarchy is defined in `imednet_sdk/exceptions.py`.
* The `BaseClient`'s request handling logic checks HTTP status codes and parses error responses.
* HTTP status codes and specific API error codes (`metadata.error.code`) are correctly mapped to the defined custom exceptions.
* Exceptions store relevant context (status code, API error code, description, field details, request path, timestamp).
* Retry logic (e.g., using `tenacity`) is implemented in the `BaseClient` for transient errors (Rate Limits, 5xx) on idempotent requests.
* Unit tests exist in `tests/test_client.py` (or a dedicated error handling test file) to verify that the correct exceptions are raised for various API error responses.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., define base exception, implement mapping for 400 errors).
2. **Write/Update Tests (TDD):**
   * Navigate to `tests/` (likely `test_client.py` or create `test_exceptions.py`).
   * Write tests that mock API responses with specific error status codes and error payloads (referencing `docs/reference/1 common.md` and `docs/reference/3 error.md`).
   * Assert that the client's request method raises the *expected* custom exception (from the hierarchy defined in the sub-tasks) when encountering these mock error responses.
   * For retry logic, test that requests are retried the correct number of times for specific transient errors and eventually succeed or raise the appropriate exception after exhausting retries.
3. **Implement Code:**
   * Define/update exception classes in `imednet_sdk/exceptions.py` as per the sub-task.
   * Modify the request handling logic within `imednet_sdk/client.py` (`BaseClient._request` or similar) to:
     * Check response status codes.
     * Parse error JSON payloads.
     * Implement the mapping logic to raise the correct custom exception based on status and error code.
     * Integrate retry logic (e.g., using `tenacity` decorator) around the request execution for applicable error types.
4. **Run Specific Tests:** `pytest tests/test_client.py -k <test_specific_error_handling>` (or relevant test file/marker).
5. **Debug & Iterate:** Fix exception definitions, client logic, or test mocks until specific tests pass.
6. **Run All Module Unit Tests:** `pytest tests/` (Ensure no regressions in other client functionality).
7. **Update Memory File:** Document the exception hierarchy, mapping logic, retry strategy, and test results in `docs/memory/06_error_handling_and_exceptions.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k <test_specific_error_handling>`
12. **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/06_error_handling_and_exceptions.md`
16. **Commit Changes:** `git commit -m "feat(core): implement exception handling for <error_type>"` or `"feat(core): add retry logic"` (Adjust scope and message).

**Sub-Tasks:**

* [ ] **Define Exception Hierarchy (`imednet_sdk/exceptions.py`):**
  * [ ] `ImednetSdkException` (base exception)
  * [ ] `ApiError(ImednetSdkException)` (for general API errors, e.g., 5xx)
  * [ ] `AuthenticationError(ImednetSdkException)` (for 401 Unauthorized)
  * [ ] `AuthorizationError(ImednetSdkException)` (for 403 Forbidden, e.g., invalid studyKey)
  * [ ] `BadRequestError(ImednetSdkException)` (for 400 Bad Request, general)
  * [ ] `ValidationError(BadRequestError)` (specifically for validation errors, code 1000)
  * [ ] `NotFoundError(ImednetSdkException)` (for 404 Not Found)
  * [ ] `RateLimitError(ImednetSdkException)` (for 429 Too Many Requests)
* [ ] **Implement Error Parsing in `BaseClient`:**
  * [ ] In the request handling logic, check the HTTP status code (>= 400).
  * [ ] Attempt to parse the JSON response body to extract `metadata.error` details.
* [ ] **Implement Exception Mapping in `BaseClient`:**
  * [ ] Map `400 BAD_REQUEST`:
    * [ ] If `metadata.error.code == "1000"`: Raise `ValidationError` (include `description`, `attribute`, `value`).
    * [ ] Otherwise: Raise `BadRequestError` (include description).
  * [ ] Map `401 UNAUTHORIZED`:
    * [ ] If `metadata.error.code == "9001"`: Raise `AuthenticationError` (invalid keys).
    * [ ] Otherwise: Raise `AuthenticationError`.
  * [ ] Map `403 FORBIDDEN`: Raise `AuthorizationError`.
  * [ ] Map `404 NOT_FOUND`: Raise `NotFoundError`.
  * [ ] Map `429 TOO_MANY_REQUESTS`: Raise `RateLimitError`.
  * [ ] Map `500 INTERNAL_SERVER_ERROR`:
    * [ ] If `metadata.error.code == "9000"`: Raise `ApiError` (Unknown Error).
    * [ ] Otherwise: Raise `ApiError`.
  * [ ] Map Other `4xx`/`5xx`: Raise generic `ApiError`.
* [ ] **Enhance Exceptions:** Ensure exceptions store context: status code, API error code, description, field details, request path, timestamp.
* [ ] **Implement Retry Logic (`BaseClient`):**
  * [ ] Use a library (e.g., `tenacity`) to add retries for `RateLimitError` and `ApiError` (5xx) on idempotent requests (GET).
  * [ ] Configure appropriate wait times (e.g., exponential backoff) and number of attempts.
