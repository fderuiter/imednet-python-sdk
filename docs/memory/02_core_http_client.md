<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\memory\\02_core_http_client.md -->
# Memory: 02 Core HTTP Client

**Date:** 2025-04-18

**Summary:**

Implemented the core `ImednetClient` class in `imednet_sdk/client.py`. This client handles basic HTTP requests (GET, POST) to the iMednet API using the `httpx` library.

**Key Features:**

* Initialization with API key, security key, base URL, default timeout, and retry configuration.
* Automatic inclusion of required authentication headers (`x-api-key`, `x-imn-security-key`).
* Internal `_request` method for handling common request logic.
* Helper methods `_get` and `_post`.
* Basic error handling for `httpx.RequestError` and `httpx.HTTPStatusError` (raising exceptions for now).
* Context manager support (`__enter__`, `__exit__`) for resource cleanup.
* Configurable request timeouts:
  * Default timeout can be set during client initialization using a float (total seconds) or an `httpx.Timeout` object.
  * Timeout can be overridden on a per-request basis in `_get` and `_post` methods.
* Configurable retry logic for transient errors:
  * Number of retries (`retries`), backoff factor (`backoff_factor`), retryable status codes (`retry_statuses`), retryable methods (`retry_methods`), and retryable exceptions (`retry_exceptions`) can be configured during client initialization.
  * Implemented exponential backoff with jitter using the `_calculate_backoff` helper method.
  * Retries are handled within the `_request` method.

**Testing:**

* Created `tests/test_client.py` using `pytest` and `respx`.
* Added tests for:
  * Client initialization.
  * Correct headers and URL construction for GET requests.
  * Correct headers, URL, and JSON payload for POST requests.
  * Handling of query parameters in GET requests.
  * Timeout configuration (defaults, custom float/object, override, exception).
  * Retry logic:
    * Success on first try.
    * Retry on configured status codes (5xx).
    * Retry on configured exceptions (`ConnectError`).
    * Exceeding retry attempts (raising original `HTTPStatusError` or `ConnectError`).
    * No retry on non-configured errors (4xx).

**Decisions:**

* Used `httpx` as the HTTP library.
* Deferred custom exception implementation to Task 06.
* Removed `_put` and `_delete` methods based on API limitations.
* Implemented configurable timeouts via `__init__` and request methods.
* Implemented configurable retry logic manually within `_request` with exponential backoff and jitter, allowing customization of retry conditions (status codes, methods, exceptions).

**Next Steps:**

* Implement specific API endpoint methods (e.g., `get_studies`).
* Refine error handling with custom exceptions (Task 06).
* Consider using `httpx`'s built-in transport/retry capabilities for potentially more robust handling if the manual approach proves insufficient.
