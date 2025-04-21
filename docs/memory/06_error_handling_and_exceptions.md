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

3. **Retry Logic Implementation:**
    * **Decision:** Chose to use the `tenacity` library instead of manual implementation.
        * **Reasoning:** `tenacity` is a mature, well-tested library providing robust features (exponential backoff, jitter, configurable conditions) out-of-the-box, reducing implementation complexity and potential bugs compared to a manual approach. The benefit outweighs the cost of adding one dependency.
    * **Dependency:** Added `tenacity>=8.0` to `pyproject.toml` and installed it using `pip install -e .`.
    * **Implementation:**
        * Refactored the `_request` method in `client.py`.
        * Removed the manual `for` loop for retries and the `_calculate_backoff` method.
        * Introduced a helper method `_make_request_attempt` containing the logic for a single request attempt (including calling `_handle_api_error`).
        * Applied the `tenacity.retry` decorator conditionally within `_request`.
        * **Configuration:**
            * `stop`: Uses `stop_after_attempt(self._retries + 1)`.
            * `wait`: Uses `wait_exponential(multiplier=self._backoff_factor, min=0.5, max=10)` for backoff with jitter (handled internally by `tenacity`).
            * `retry`: Uses `retry_if_exception_type(tuple(self._retry_exceptions))`. The default `_retry_exceptions` set includes `RateLimitError`, `ApiError` (for 5xx), and common `httpx.RequestError` types (like `ConnectError`, `ReadTimeout`). This set is configurable during client initialization.
            * `reraise`: Set to `True` to ensure the original exception is raised after exhausting retries.
        * **Condition:** Retries are only applied if the HTTP `method` is in the `_retry_methods` set (defaults to `{"GET"}`, configurable during client initialization), aligning with the requirement to only retry idempotent operations.

## Next Steps (Based on Task 06)

* Write unit tests in `tests/test_client.py` (or a dedicated file) to verify:
  * Correct custom exceptions are raised for various mocked API error responses (status codes, error codes, payloads).
  * Retry logic functions as expected (requests are retried for configured exceptions/methods, correct number of times, correct final exception raised).
* Update `docs/todo/06_error_handling_and_exceptions.md` checklist.
