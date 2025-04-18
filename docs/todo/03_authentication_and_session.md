<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\todo\\03_authentication_and_session.md -->
# Task 03: Authentication and Session Management

**Objective:** Ensure the client handles API credentials securely and injects required headers into all requests.

**Key Requirements & Sub-Tasks:**

* [x] **Implement credential handling (Initialization & Environment Variables).**
  * [x] **Identify Task:** Allow API Key and Security Key via `__init__` and environment variables.
  * [x] **Write/Update Tests:** Add tests to `tests/test_client.py` to:
    * [x] Verify client initialization with explicit keys.
    * [x] Verify client initialization reads keys from `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` environment variables if not passed explicitly.
    * [x] Verify explicit keys override environment variables.
    * [x] Verify `AuthenticationError` (to be created in Task 06) is raised if keys are missing from both sources.
  * [x] **Implement Code:**
    * [x] Modify `ImednetClient.__init__` in `imednet_sdk/client.py`.
    * [x] Use `os.getenv()` to read environment variables.
    * [x] Store the keys securely within the client instance (avoid logging).
    * [x] Implement the logic to prioritize explicit arguments over environment variables.
    * [x] Add a check to raise `AuthenticationError` if keys are ultimately missing (placeholder for now, actual exception in Task 06).
  * [x] **Run Specific Tests:** `pytest tests/test_client.py -k credential` (used `-k initialization`)
  * [x] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document credential handling logic in `docs/memory/03_authentication_and_session.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k credential` (used `-k initialization`)
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): implement credential handling via init and env vars\"`

* [x] **Implement automatic header injection.**
  * [x] **Identify Task:** Inject `x-api-key`, `x-imn-security-key`, `Accept`, and `Content-Type` headers.
  * [x] **Write/Update Tests:** Update tests in `tests/test_client.py` (potentially reusing tests from Task 02) to verify:
    * [x] `x-api-key` header is present with the correct value.
    * [x] `x-imn-security-key` header is present with the correct value.
    * [x] `Accept: application/json` header is present.
    * [x] `Content-Type: application/json` header is present on relevant requests (e.g., POST).
  * [x] **Implement Code:**
    * [x] Modify the `_request` method (or equivalent) in `imednet_sdk/client.py`.
    * [x] Ensure the `httpx.Client` is configured with these base headers or add them dynamically before sending each request. (Done via `httpx.Client` init).
    * [x] Refer to `docs/reference/1 common.md` and `docs/reference/2 header.md` for confirmation.
  * [x] **Run Specific Tests:** `pytest tests/test_client.py -k header`
  * [x] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document header injection logic in `docs/memory/03_authentication_and_session.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k header`
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): implement automatic header injection\"`

* [x] **Validate key presence before requests.**
  * [x] **Identify Task:** Ensure keys are validated before making API calls.
  * [x] **Write/Update Tests:** (Covered by credential handling tests - verify `AuthenticationError` is raised appropriately).
  * [x] **Implement Code:**
    * [x] Ensure the check implemented in the first sub-task correctly prevents requests if keys are missing.
    * [x] This might involve placing the check within `_request` or ensuring `__init__` fails early. (Done in `__init__`).
  * [x] **Run Specific Tests:** `pytest tests/test_client.py -k credential` (used `-k initialization`)
  * [x] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document validation logic in `docs/memory/03_authentication_and_session.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k credential` (used `-k initialization`)
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"refactor(client): ensure key validation before requests\"`

* [x] **Consider thread-safety (if applicable).**
  * [x] **Identify Task:** Analyze if the current `httpx.Client` usage is thread-safe.
  * [x] **Write/Update Tests:** (Difficult to test reliably with unit tests). Manual analysis or specific integration tests might be needed if multi-threading is a primary use case.
  * [x] **Implement Code:**
    * [x] Research `httpx` thread-safety guarantees. Generally, `httpx.Client` is thread-safe for requests but not for configuration changes after initialization.
    * [x] If modifications are needed (e.g., using thread-local storage or ensuring client instances are not shared inappropriately across threads), implement them. (No changes needed).
  * [x] **Run Specific Tests:** (Manual analysis or specific tests)
  * [x] **Debug & Iterate:** Fix implementation based on analysis.
  * [x] **Run All Module Unit Tests:** `pytest tests/`
  * [x] **Update Memory File:** Document thread-safety considerations and implementation details in `docs/memory/03_authentication_and_session.md`.
  * [x] **Stage Changes:** `git add .`
  * [x] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [x] **Fix Pre-commit Issues:** Address any reported issues.
  * [x] **Re-run Specific Tests (Post-Fix):** (Manual analysis or specific tests)
  * [x] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [x] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [x] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"chore(client): analyze and ensure thread-safety\"`

**Acceptance Criteria:**

* [x] Client can be initialized with keys passed directly or read from environment variables.
* [x] An appropriate error (`ValueError` currently) is raised if keys are missing.
* [x] All required headers (`x-api-key`, `x-imn-security-key`, `Accept`, `Content-Type`) are automatically included in requests.
* [x] Client usage is confirmed to be thread-safe for intended use cases.

**Notes:**

* The actual `AuthenticationError` exception class will be defined in Task 06.
* Security considerations (avoiding logging keys) should be maintained throughout.
