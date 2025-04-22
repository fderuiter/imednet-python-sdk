<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\todo\\02_core_http_client.md -->
# Task 02: Core HTTP Client
<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\todo\\02_core_http_client.md -->

**Status:** Basic Implementation Complete (Further refinement needed for error handling, retries, timeouts)

**Objective:** Implement the core HTTP client responsible for making requests to the iMednet API.

**Key Requirements & Sub-Tasks:**

* [x] **Use `httpx` for making HTTP requests.**
  * [x] Add `httpx` to `requirements.txt` and `pyproject.toml`.
  * [x] Implement basic client structure using `httpx.Client` or `httpx.AsyncClient`.
* [x] **Handle base URL configuration.**
  * [x] Add `base_url` parameter to `ImednetClient.__init__`.
  * [x] Provide a default production URL.
  * [x] Write tests (`tests/test_client.py`) for base URL initialization.
  * [x] Implement the configuration logic in `imednet_sdk/client.py`.
  * [x] Run tests, debug, and iterate until tests pass.
  * [x] Update `docs/memory/02_core_http_client.md`.
  * [x] Stage, run pre-commit, fix issues, re-test, stage again, mark task done, commit.
* [x] **Include necessary authentication headers automatically.**
  * [x] Add `api_key` and `imn_security_key` parameters to `ImednetClient.__init__`.
  * [x] Store credentials in the client instance.
  * [x] Write tests (`tests/test_client.py`) to verify headers are added to requests.
  * [x] Modify request methods in `imednet_sdk/client.py` to inject `x-api-key` and `x-imn-security-key` headers.
  * [x] Run tests, debug, and iterate until tests pass.
  * [x] Update `docs/memory/02_core_http_client.md`.
  * [x] Stage, run pre-commit, fix issues, re-test, stage again, mark task done, commit.
* [x] **Provide methods for common HTTP verbs (GET, POST).** (PUT/DELETE removed as not supported by API).
  * [x] Define `_request`, `get`, and `post` methods in `ImednetClient`.
  * [x] Write basic tests (`tests/test_client.py`) for GET and POST requests using `requests-mock` or similar.
  * [x] Implement the `get` and `post` methods in `imednet_sdk/client.py`, calling the underlying `httpx` client.
  * [x] Run tests, debug, and iterate until tests pass.
  * [x] Update `docs/memory/02_core_http_client.md`.
  * [x] Stage, run pre-commit, fix issues, re-test, stage again, mark task done, commit.
* [x] **Basic error handling for connection issues and non-2xx status codes.**
  * [x] Initial implementation relies on `httpx` raising its exceptions (e.g., `httpx.RequestError`, `httpx.HTTPStatusError`). Refinement in Task 06.
  * [x] Write tests (`tests/test_client.py`) for expected `httpx` exceptions on network errors or bad status codes.
  * [x] Ensure the client correctly propagates these exceptions.
  * [x] Run tests, debug, and iterate until tests pass.
  * [x] Update `docs/memory/02_core_http_client.md`.
  * [x] Stage, run pre-commit, fix issues, re-test, stage again, mark task done, commit.
* [x] **Implement configurable request timeouts.**
  * [x] **Identify Task:** Implement configurable timeouts.
  * [x] **Write/Update Tests:** Add tests to `tests/test_client.py` to:
    * [x] Verify default timeout is used if none is provided.
    * [x] Verify a custom timeout passed during client initialization is used.
    * [x] Verify a timeout passed directly to a request method (e.g., `get(..., timeout=...)`) overrides the client default.
    * [x] Verify `httpx.TimeoutException` is raised when a timeout occurs.
  * [x] **Implement Code:**
    * [x] Add a `timeout` parameter to `ImednetClient.__init__` with a reasonable default (e.g., `httpx.Timeout(10.0)`).
    * [x] Store the timeout configuration in the client instance.
    * [x] Pass the configured timeout to the underlying `httpx.Client` upon its initialization or to individual requests.
    * [x] Allow overriding the timeout on a per-request basis in `get`/`post` methods.
  * [x] **Run Specific Tests:** `pytest tests/test_client.py -k timeout`
  * [x] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document timeout implementation details in `docs/memory/02_core_http_client.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k timeout`
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done: `[x] Implement configurable request timeouts.`
  * [x] **Commit Changes:** `git commit -m \"feat(client): implement configurable request timeouts\"`
* [x] **Implement retry logic for transient errors (e.g., 5xx, network errors).**
  * [x] **Identify Task:** Implement retry logic.
  * [x] **Write/Update Tests:** Add tests to `tests/test_client.py` to:
    * [x] Verify successful request occurs without retries on 2xx status.
    * [x] Verify retries happen for configured transient errors (e.g., 500, 503, `httpx.RequestError`).
    * [x] Verify the correct number of retries are attempted based on configuration.
    * [x] Verify backoff delay occurs between retries (if implemented).
    * [x] Verify the original error is raised after all retries fail.
  * [x] **Implement Code:**
    * [x] Consider using `httpx`'s built-in transport/retry capabilities or a library like `tenacity`.
    * [x] Add configuration parameters to `ImednetClient.__init__` (e.g., `retries=3`, `retry_statuses=[500, 503]`, `backoff_factor=0.5`).
    * [x] Integrate the retry mechanism into the `_request` method or `httpx.Client` setup.
  * [x] **Run Specific Tests:** `pytest tests/test_client.py -k retry`
  * [x] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document retry implementation details in `docs/memory/02_core_http_client.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k retry`
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done: `[x] Implement retry logic...`
  * [x] **Commit Changes:** `git commit -m \"feat(client): implement retry logic for transient errors\"`
* [x] **Support context manager protocol (`with` statement) for cleanup.**
  * [x] Implement `__enter__` and `__exit__` (or `__aenter__`/`__aexit__` if async) in `ImednetClient`.
  * [x] Ensure `__exit__` calls the underlying `httpx.Client.close()` method.
  * [x] Write tests (`tests/test_client.py`) to verify the client can be used in a `with` statement and that `close()` is called.
  * [x] Run tests, debug, and iterate until tests pass.
  * [x] Update `docs/memory/02_core_http_client.md`.
  * [x] Stage, run pre-commit, fix issues, re-test, stage again, mark task done, commit.

**Acceptance Criteria:**

* [x] Client can be initialized with credentials and base URL.
* [x] GET requests can be made successfully.
* [x] POST requests with JSON payloads can be made successfully.
* [x] Basic tests exist for initialization, GET, and POST requests.
* [x] Tests exist for timeout configuration and functionality.
* [x] Tests exist for retry logic functionality.
* [x] Client works correctly within a `with` statement.

**Notes:**

* Error handling refinement (custom exceptions) is planned for Task 06.
