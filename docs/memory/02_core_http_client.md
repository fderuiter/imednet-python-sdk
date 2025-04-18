# Memory: 02 Core HTTP Client

**Date:** 2025-04-18

**Summary:**

Implemented the core `ImednetClient` class in `imednet_sdk/client.py`. This client handles basic HTTP requests (GET, POST) to the iMednet API using the `httpx` library.

**Key Features:**

* Initialization with API key, security key, base URL, and timeout.
* Automatic inclusion of required authentication headers (`x-api-key`, `x-imn-security-key`).
* Internal `_request` method for handling common request logic.
* Helper methods `_get` and `_post`.
* Basic error handling for `httpx.RequestError` and `httpx.HTTPStatusError` (raising exceptions for now).
* Context manager support (`__enter__`, `__exit__`) for resource cleanup.

**Testing:**

* Created `tests/test_client.py` using `pytest` and `respx`.
* Added tests for:
  * Client initialization.
  * Correct headers and URL construction for GET requests.
  * Correct headers, URL, and JSON payload for POST requests.
  * Handling of query parameters in GET requests.
* Skipped tests for timeout and retry logic (to be implemented later).
* Added tests for timeout configuration (`test_request_timeout_custom`) and retry logic on server errors (`test_retry_logic_on_failure`).
  * Initial timeout assertion required fixing attribute access (`connect` and `read`).
  * Retry test simulated a 503 then 200 response to verify retry attempts.

**Decisions:**

* Used `httpx` as the HTTP library for its modern features and async support (though currently using the sync client).
* Decided to raise exceptions directly in `_request` for now, deferring custom exception implementation to the dedicated error handling task.
* Removed `_put` and `_delete` methods and corresponding tests based on API limitations.
* Implemented configurable timeouts and retry loop for 5xx errors in `_request`, balancing simplicity and reliability.

**Next Steps:**

* Implement specific API endpoint methods (e.g., `get_studies`).
* Refine error handling with custom exceptions.
