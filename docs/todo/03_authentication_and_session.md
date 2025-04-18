# Task 03: Authentication and Session Management
<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\todo\\03_authentication_and_session.md -->

**Objective:** Ensure the client handles API credentials securely and injects required headers into all requests.

**Key Requirements & Sub-Tasks:**

* [ ] **Implement credential handling (Initialization & Environment Variables).**
  * [ ] **Identify Task:** Allow API Key and Security Key via `__init__` and environment variables.
  * [ ] **Write/Update Tests:** Add tests to `tests/test_client.py` to:
    * [ ] Verify client initialization with explicit keys.
    * [ ] Verify client initialization reads keys from `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` environment variables if not passed explicitly.
    * [ ] Verify explicit keys override environment variables.
    * [ ] Verify `AuthenticationError` (to be created in Task 06) is raised if keys are missing from both sources.
  * [ ] **Implement Code:**
    * [ ] Modify `ImednetClient.__init__` in `imednet_sdk/client.py`.
    * [ ] Use `os.getenv()` to read environment variables.
    * [ ] Store the keys securely within the client instance (avoid logging).
    * [ ] Implement the logic to prioritize explicit arguments over environment variables.
    * [ ] Add a check to raise `AuthenticationError` if keys are ultimately missing (placeholder for now, actual exception in Task 06).
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py -k credential`
  * [ ] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document credential handling logic in `docs/memory/03_authentication_and_session.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k credential`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): implement credential handling via init and env vars\"`

* [ ] **Implement automatic header injection.**
  * [ ] **Identify Task:** Inject `x-api-key`, `x-imn-security-key`, `Accept`, and `Content-Type` headers.
  * [ ] **Write/Update Tests:** Update tests in `tests/test_client.py` (potentially reusing tests from Task 02) to verify:
    * [ ] `x-api-key` header is present with the correct value.
    * [ ] `x-imn-security-key` header is present with the correct value.
    * [ ] `Accept: application/json` header is present.
    * [ ] `Content-Type: application/json` header is present on relevant requests (e.g., POST).
  * [ ] **Implement Code:**
    * [ ] Modify the `_request` method (or equivalent) in `imednet_sdk/client.py`.
    * [ ] Ensure the `httpx.Client` is configured with these base headers or add them dynamically before sending each request.
    * [ ] Refer to `docs/reference/1 common.md` and `docs/reference/2 header.md` for confirmation.
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py -k header`
  * [ ] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document header injection logic in `docs/memory/03_authentication_and_session.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k header`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): implement automatic header injection\"`

* [ ] **Validate key presence before requests.**
  * [ ] **Identify Task:** Ensure keys are validated before making API calls.
  * [ ] **Write/Update Tests:** (Covered by credential handling tests - verify `AuthenticationError` is raised appropriately).
  * [ ] **Implement Code:**
    * [ ] Ensure the check implemented in the first sub-task correctly prevents requests if keys are missing.
    * [ ] This might involve placing the check within `_request` or ensuring `__init__` fails early.
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py -k credential`
  * [ ] **Debug & Iterate:** Fix implementation or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document validation logic in `docs/memory/03_authentication_and_session.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py -k credential`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"refactor(client): ensure key validation before requests\"`

* [ ] **Consider thread-safety (if applicable).**
  * [ ] **Identify Task:** Analyze if the current `httpx.Client` usage is thread-safe.
  * [ ] **Write/Update Tests:** (Difficult to test reliably with unit tests). Manual analysis or specific integration tests might be needed if multi-threading is a primary use case.
  * [ ] **Implement Code:**
    * [ ] Research `httpx` thread-safety guarantees. Generally, `httpx.Client` is thread-safe for requests but not for configuration changes after initialization.
    * [ ] If modifications are needed (e.g., using thread-local storage or ensuring client instances are not shared inappropriately across threads), implement them.
  * [ ] **Run Specific Tests:** (Manual analysis or specific tests)
  * [ ] **Debug & Iterate:** Fix implementation based on analysis.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document thread-safety considerations and implementation details in `docs/memory/03_authentication_and_session.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** (Manual analysis or specific tests)
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"chore(client): analyze and ensure thread-safety\"`

**Acceptance Criteria:**

* [ ] Client can be initialized with keys passed directly or read from environment variables.
* [ ] An appropriate error (`AuthenticationError`) is raised if keys are missing.
* [ ] All required headers (`x-api-key`, `x-imn-security-key`, `Accept`, `Content-Type`) are automatically included in requests.
* [ ] Client usage is confirmed to be thread-safe for intended use cases.

**Notes:**

* The actual `AuthenticationError` exception class will be defined in Task 06.
* Security considerations (avoiding logging keys) should be maintained throughout.
