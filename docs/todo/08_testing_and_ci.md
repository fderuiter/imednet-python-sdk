# Task 08: Testing Strategy and Automation

**Objective:** Establish a comprehensive testing strategy using `pytest`, implement unit tests with mocking, configure code coverage reporting, and set up a Continuous Integration (CI) pipeline using GitHub Actions.

**Definition of Done:**

* `pytest` is configured as the test runner.
* Required testing dependencies are added to `requirements-dev.txt`.
* A `tests/` directory structure mirroring `imednet_sdk/` exists.
* Unit tests cover Pydantic models, resource client methods (including success, errors, parameters), and `BaseClient` functionality.
* `requests-mock` or equivalent is used for mocking HTTP interactions.
* `pytest` fixtures are used for setup (clients, mock data).
* Code coverage is measured and configured (e.g., via `pytest-cov`).
* A GitHub Actions workflow (`.github/workflows/ci.yml`) is created and functional.
* The CI workflow runs linters, type checks, tests (across multiple Python versions), and optionally uploads coverage reports.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., set up pytest, write model tests, create CI workflow).
2. **Write/Update Tests (TDD - where applicable):**
   * For sub-tasks involving writing test code (e.g., model tests, client tests): Navigate to the relevant `tests/` subdirectory.
   * Create or modify test files (e.g., `test_models.py`, `test_studies.py`).
   * Write tests that assert the expected behavior based on the sub-task requirements (e.g., model parsing, correct exception raised, correct API call parameters).
   * Use mock data and HTTP mocking where necessary.
   * For configuration tasks (e.g., setting up pytest, CI), the "test" is verifying the configuration works as expected in later steps.
3. **Implement Code/Configuration:**
   * Install necessary packages and update `requirements-dev.txt`.
   * Create/modify source files (`imednet_sdk/`) or test files (`tests/`) as needed.
   * Create/modify configuration files (e.g., `pyproject.toml` for pytest/coverage, `.github/workflows/ci.yml`).
4. **Run Specific Tests/Checks:**
   * For test code: `pytest tests/<relevant_path>/test_*.py -k <specific_test>`
   * For CI setup: Manually trigger or push to trigger the workflow and check its execution.
   * For coverage setup: `pytest --cov=imednet_sdk` and check the report.
5. **Debug & Iterate:** Fix implementation, configuration, or tests until the specific checks pass.
6. **Run All Applicable Tests/Checks:**
   * Run the full test suite: `pytest`
   * Run linters/formatters/type checks locally: `pre-commit run --all-files` (or individual tools like `black .`, `flake8 .`, `mypy .`)
   * Verify the CI workflow passes on a push/PR.
7. **Update Memory File:** Document the setup, configurations, test strategies, CI workflow details, and results in `docs/memory/07_testing_and_ci.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Tests/Checks (Post-Fix):** Verify fixes didn't break functionality (Step 4).
12. **Re-run All Applicable Tests/Checks (Post-Fix - Optional):** Verify overall integrity (Step 6).
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/07_testing_and_ci.md`
16. **Commit Changes:** `git commit -m "feat(test): <description_of_subtask>"` or `"ci: <description_of_subtask>"` (Adjust type/scope and message).

**Sub-Tasks:**

* [ ] **Setup `pytest` and Dependencies:**
  * [ ] Install `pytest`, `pytest-cov`, `requests-mock` (or `respx`).
  * [ ] Add dependencies to `requirements-dev.txt`.
  * [ ] Configure `pytest` options if needed (e.g., in `pyproject.toml`).
* [ ] **Create Test Directory Structure:**
  * [ ] Create `tests/` mirroring `imednet_sdk/` (e.g., `tests/api/`, `tests/models/`).
  * [ ] Add `__init__.py` files as needed.
* [ ] **Implement Unit Tests - Models (`tests/models/`):**
  * [ ] Test Pydantic model serialization/deserialization using sample JSON.
  * [ ] Test successful parsing (nested structures, dates).
  * [ ] Test handling of optional/null fields.
  * [ ] Test validation errors for incorrect data.
* [ ] **Implement Unit Tests - Resource Clients (`tests/api/`):**
  * [ ] Use `requests-mock` (or equivalent) for mocking.
  * [ ] For each client method:
    * [ ] Mock successful responses (2xx) with sample data.
    * [ ] Assert correct URL, method, headers, query params are used.
    * [ ] Assert correct request body serialization (for POST/PUT).
    * [ ] Assert correct response deserialization to Pydantic models.
    * [ ] Test pagination, filtering, sorting variations.
* [ ] **Implement Unit Tests - Error Handling:**
  * [ ] Mock API error responses (4xx, 5xx) with error payloads.
  * [ ] Assert correct custom exceptions (Task 6) are raised.
  * [ ] Assert exceptions contain relevant details.
* [ ] **Implement Unit Tests - `BaseClient`:**
  * [ ] Test header injection (`x-api-key`, etc.).
  * [ ] Test URL building logic.
  * [ ] Test retry logic (if implemented in Task 6).
* [ ] **Implement Fixtures (`tests/conftest.py`):**
  * [ ] Create fixtures for initialized clients.
  * [ ] Create fixtures for mock API keys.
  * [ ] Create fixtures or helpers to load sample JSON response data (e.g., from `tests/fixtures/`).
* [ ] **Configure Code Coverage:**
  * [ ] Configure `pytest-cov` (e.g., in `pyproject.toml` or `setup.cfg`).
  * [ ] Set a coverage threshold goal (e.g., >90%).
* [ ] **Set up Continuous Integration (CI - GitHub Actions):**
  * [ ] Create `.github/workflows/ci.yml`.
  * [ ] Configure jobs to:
    * [ ] Checkout code.
    * [ ] Set up Python matrix (e.g., 3.8, 3.9, 3.10, 3.11, 3.12).
    * [ ] Install dependencies.
    * [ ] Run linters/formatters (via pre-commit or directly).
    * [ ] Run type checks (`mypy`).
    * [ ] Run tests with coverage (`pytest --cov=imednet_sdk`).
    * [ ] (Optional) Add step to enforce coverage threshold.
    * [ ] (Optional) Upload coverage reports (e.g., Codecov).
* [ ] **Integration Tests (Optional):**
  * [ ] Consider adding tests against a sandbox environment or using `vcrpy`.
