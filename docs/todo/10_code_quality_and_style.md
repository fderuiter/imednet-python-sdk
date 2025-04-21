# Task 10: Code Quality and Style Enforcement

**Objective:** Configure and enforce consistent code style, formatting, linting, and type checking using automated tools and pre-commit hooks.

**Definition of Done:**

* Black, Flake8, isort, and mypy are configured for the project.
* The entire codebase adheres to the configured styles and passes all checks.
* An `.editorconfig` file ensures consistent editor settings.
* `pre-commit` hooks are set up and installed for Black, Flake8, isort, mypy, and common checks.
* `docs/coding_standards.md` is updated to reflect the chosen tools and configurations.
* The CI workflow (Task 7) includes steps to enforce these quality checks.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., configure Black, set up pre-commit).
2. **Write/Update Tests (TDD - N/A):**
   * Testing for this task involves running the configured tools and verifying they pass or report expected issues.
3. **Implement Code/Configuration:**
   * Install necessary tools (`pip install black flake8 isort mypy pre-commit ...`), add to `requirements-dev.txt`.
   * Create/modify configuration files (`pyproject.toml`, `.flake8`, `.isort.cfg`, `mypy.ini`, `.editorconfig`, `.pre-commit-config.yaml`).
   * Add/update type hints in the codebase (`imednet_sdk/**/*.py`).
   * Run formatters/sorters initially to fix existing code (`black .`, `isort .`).
   * Install pre-commit hooks (`pre-commit install`).
   * Update `docs/coding_standards.md`.
   * Update CI workflow (`.github/workflows/ci.yml`) to include check steps.
4. **Run Specific Checks:**
   * Run the specific tool being configured (e.g., `black --check .`, `flake8 .`, `isort --check .`, `mypy .`).
   * For pre-commit, stage files and run `pre-commit run` or `git commit` to trigger hooks.
   * For CI, push changes and check the workflow run.
5. **Debug & Iterate:** Fix configuration issues, code style violations, type errors, or CI workflow steps until the checks pass.
6. **Run All Applicable Checks:**
   * Run all checks via pre-commit: `pre-commit run --all-files`.
   * Verify the CI workflow passes with all quality checks included.
7. **Update Memory File:** Document the chosen tools, configurations, pre-commit setup, CI integration details, and results in `docs/memory/09_code_quality_and_style.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files` (This should now pass if Step 6 was successful).
10. **Fix Pre-commit Issues:** Address any remaining issues (should be minimal if Step 6 passed).
11. **Re-run Specific Checks (Post-Fix):** Verify fixes (Step 4).
12. **Re-run All Applicable Checks (Post-Fix - Optional):** Verify overall integrity (Step 6).
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/09_code_quality_and_style.md`
16. **Commit Changes:** `git commit -m "style: configure <tool_name>"` or `"ci: add <tool_name> checks"` or `"refactor: apply formatting/linting fixes"` (Adjust type/scope and message).

**Sub-Tasks:**

* [ ] **Formatter (Black):**
  * [ ] Install Black.
  * [ ] Configure Black (e.g., `pyproject.toml`).
  * [ ] Apply Black formatting (`black .`).
* [ ] **Linter (Flake8):**
  * [ ] Install Flake8 and plugins (e.g., `flake8-bugbear`, `flake8-comprehensions`).
  * [ ] Configure Flake8 (e.g., `setup.cfg`, `.flake8`).
  * [ ] Address linting errors/warnings (`flake8 .`).
* [ ] **Import Sorting (isort):**
  * [ ] Install isort.
  * [ ] Configure isort (e.g., `pyproject.toml`).
  * [ ] Apply isort (`isort .`).
* [ ] **Type Checking (mypy):**
  * [ ] Install mypy.
  * [ ] Configure mypy (e.g., `mypy.ini`, `pyproject.toml`), aim for strictness.
  * [ ] Add/update type hints throughout the codebase.
  * [ ] Address mypy errors (`mypy .`).
* [ ] **EditorConfig:**
  * [ ] Create/verify `.editorconfig` for consistent editor settings.
* [ ] **Pre-commit Hooks:**
  * [ ] Install pre-commit.
  * [ ] Create/configure `.pre-commit-config.yaml`.
  * [ ] Add hooks for `black`, `flake8`, `isort`, `mypy`.
  * [ ] Add common hooks (`check-yaml`, `end-of-file-fixer`, etc.).
  * [ ] Install hooks (`pre-commit install`).
* [ ] **Coding Standards Document:**
  * [ ] Update `docs/coding_standards.md` with tool choices and configurations.
* [ ] **CI Integration:**
  * [ ] Add steps to CI workflow (Task 7) to run Black (`--check`), Flake8, isort (`--check`), and mypy.
