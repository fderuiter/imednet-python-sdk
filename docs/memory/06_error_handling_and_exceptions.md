<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\memory\06_error_handling_and_exceptions.md -->
# Memory Log: Task 06 - Error Handling and Exceptions

**Date:** 2025-04-21

**Objective:** Define and implement a robust error handling mechanism using custom exceptions mapped from API responses, including retry logic for transient errors.

## Decisions & Implementation Details

1. **Custom Exception Hierarchy:**
   * Defined a hierarchy of custom exceptions inheriting from `ImednetSdkException` in `imednet_sdk/exceptions.py`.
   * Includes specific exceptions like `ApiError`, `AuthenticationError`, `AuthorizationError`, `BadRequestError`, `ValidationError`, `NotFoundError`, and `RateLimitError`.
   * The base exception and specific ones store context like `status_code`, `api_error_code`, `request_path`, `response_body`, and `timestamp`. `ValidationError` additionally stores `attribute` and `value`.

2. **Error Parsing & Mapping:**
   * Implemented the `_handle_api_error` method within `ImednetClient` (`imednet_sdk/client.py`).
   * This method attempts to parse the JSON error response from the API (`metadata.error`).
   * It maps HTTP status codes (4xx/5xx) and specific `metadata.error.code` values (e.g., "1000" for validation, "9001" for auth) to the corresponding custom exceptions defined above.
   * If parsing fails or codes don't match specific cases, it falls back to more general exceptions (`BadRequestError`, `ApiError`).
   * The `_request` method now calls `_handle_api_error` for any non-2xx response *before* attempting to process a successful response.

3. **Retry Logic Implementation (using `tenacity`):**
   * **Dependency:** Added `tenacity>=8.0` to `pyproject.toml`.
   * **Refactoring:**
     * Refactored the `_request` method in `client.py`.
     * Removed the manual `for` loop for retries and the `_calculate_backoff` method.
     * Introduced a helper method `_make_request_attempt` containing the logic for a single request attempt (including calling `_handle_api_error`).
     * Applied the `tenacity.retry` decorator conditionally within `_request` based on the HTTP method.
   * **Configuration:**
     * `stop`: Uses `stop_after_attempt(self._retries + 1)`.
     * `wait`: Uses `wait_exponential(multiplier=self._backoff_factor, min=0.5, max=10)`.
     * `retry`: Uses `retry_if_exception_type(tuple(self._retry_exceptions_tuple))`. The default `_retry_exceptions_tuple` includes `RateLimitError`, `ApiError` (for 5xx), and common `httpx.RequestError` types. Configurable during client initialization.
     * `reraise`: Set to `True`.
   * **Condition:** Retries only applied if the HTTP `method` is in the `_retry_methods` set (defaults to `{"GET"}`).

4. **Unit Testing (`tests/test_client.py`):**
   * Added comprehensive tests for the custom exception mapping logic in `_handle_api_error`:
     * Verified correct exceptions (`ValidationError`, `BadRequestError`, `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `RateLimitError`, `ApiError`) are raised for corresponding status codes and API error codes (e.g., 400/1000 -> `ValidationError`, 401/9001 -> `AuthenticationError`, 429 -> `RateLimitError`, 503 -> `ApiError`).
     * Tested edge cases like non-JSON error responses.
     * Asserted that exception attributes (`status_code`, `api_error_code`, `message`, `attribute`, `value`, etc.) are populated correctly.
   * Added tests specifically for the `tenacity` retry logic:
     * Verified successful retries on GET requests for `RateLimitError` (429), `ApiError` (5xx), and `httpx.ReadTimeout`.
     * Verified that the correct exception (`RateLimitError`, `ApiError`) is raised after exhausting retry attempts on GET requests.
     * Verified that retries are *not* attempted by default for non-idempotent methods (e.g., POST) even on retryable exceptions (`RateLimitError`).
     * Verified that retries are *not* attempted for non-retryable exceptions (`AuthenticationError`, `NotFoundError`) even on GET requests.
   * **Test Fixes (2025-04-21):**
     * Corrected an `ImportError` by changing `SdkValidationError` to the correct `ValidationError` in the test file imports.
     * Fixed an `AssertionError` in `test_get_deserialization_validation_error` by ensuring the test checks for `pydantic.ValidationError` (aliased as `PydanticValidationError`) as the underlying cause when testing Pydantic model validation failures, rather than the custom SDK `ValidationError`.

## Next Steps (Based on Task 06)

* [x] Write unit tests in `tests/test_client.py` to verify:
  * [x] Correct custom exceptions are raised for various mocked API error responses.
  * [x] Retry logic functions as expected (requests are retried for configured exceptions/methods, correct number of times, correct final exception raised).
* Update `docs/todo/06_error_handling_and_exceptions.md` checklist.
