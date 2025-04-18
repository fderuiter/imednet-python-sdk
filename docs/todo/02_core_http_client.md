# Task 02: Core HTTP Client

**Status:** Basic Implementation Complete (Further refinement needed for error handling, retries)

**Objective:** Implement the core HTTP client responsible for making requests to the iMednet API.

**Key Requirements:**

* [x] Use `httpx` for making HTTP requests.
* [x] Handle base URL configuration (defaulting to production).
* [x] Include necessary authentication headers (`x-api-key`, `x-imn-security-key`) automatically.
* [x] Provide methods for common HTTP verbs (GET, POST - PUT/DELETE removed as not supported).
* [x] Basic error handling for connection issues and non-2xx status codes (currently raises `httpx` exceptions).
* [ ] Implement configurable request timeouts.
* [ ] Implement retry logic for transient errors (e.g., 5xx).
* [x] Support context manager protocol (`with` statement) for cleanup.

**Acceptance Criteria:**

* [x] Client can be initialized with credentials and base URL.
* [x] GET requests can be made successfully.
* [x] POST requests with JSON payloads can be made successfully.
* [x] Basic tests exist for initialization, GET, and POST requests.
* [ ] Tests exist for timeout configuration.
* [ ] Tests exist for retry logic.

**Notes:**

* Error handling will be further refined in Task 06.
* Timeout and retry logic implementation deferred.
