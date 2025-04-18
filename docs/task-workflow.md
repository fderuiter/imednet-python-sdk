# Standard Development Workflow

This document outlines the standardized step-by-step process for implementing features and fixes in this project, ensuring consistency and quality through Test-Driven Development (TDD) and pre-commit checks.

## Workflow Steps

1. **Identify Task:**
    * Select the next subtask from the relevant `docs/todo/` file (e.g., `01-*.md`).
    * Review the task context, goals, and definition of done.

2. **Write/Update Tests (TDD):**
    * Navigate to the corresponding test directory (e.g., `tests/unit/*/`).
    * Create or modify the relevant test file (e.g., `test_feature*.py`).
    * Write new unit tests or update existing ones based on the task requirements.
    * **TDD Principle:** Tests should initially fail or assert `NotImplementedError` if the code doesn't exist yet.

3. **Implement Code:**
    * Navigate to the corresponding source directory (e.g., `src/*/`).
    * Create or modify the relevant source file (e.g., `feature*.py`).
    * Write the necessary code to fulfill the task requirements and make the tests pass.

4. **Run Specific Tests:**
    * Execute the unit tests directly related to the changes made.
    * Example: `pytest tests/unit/*/test_feature.py`

5. **Debug & Iterate:**
    * If specific tests fail, debug the implementation code and/or the test logic.
    * Repeat steps 3 (Implement Code) and 4 (Run Specific Tests) until the specific tests pass.

6. **Run All Module Unit Tests (Regression Check):**
    * Execute all unit tests within the affected module to ensure no existing functionality was broken.
    * Example: `pytest tests/unit/*/`
    * *(Optional but recommended: Run the full unit test suite: `pytest tests/unit/`)*
    * Fix any regressions found, re-running tests as needed.

7. **Update Memory File:**
    * Open the relevant memory file (e.g., `docs/memory/01-*.md`). Note the name of the memory file will match the task number.
    * Append a new section for the completed subtask.
    * Document the implementation details, test results (including initial failures and final success), and any significant fixes or decisions made.

8. **Stage Changes:**
    * Add all modified and newly created files to the Git staging area.
    * Command: `git add .`

9. **Run Pre-commit Checks:**
    * Execute the pre-commit hooks against all staged files to check for formatting, linting, and other quality issues.
    * Command: `pre-commit run --all-files` (or just `pre-commit run` if only staged files need checking).

10. **Fix Pre-commit Issues:**
    * If any pre-commit checks fail, review the error messages.
    * Apply the necessary fixes (e.g., reformatting code, removing unused imports).
    * *Self-Correction:* Some tools might automatically fix issues.

11. **Re-run Specific Tests (Post-Fix):**
    * After fixing pre-commit issues, re-run the specific unit tests related to the current task (Step 4) to ensure the fixes didn't inadvertently break the core functionality.
    * Fix any new issues found.

12. **Re-run All Module Unit Tests (Post-Fix - Optional):**
    * Optionally, re-run the module's unit tests (Step 6) again for extra confidence.

13. **Update Memory File (Post-Fix):**
    * If any significant fixes were made during steps 10-12, briefly update the memory file entry for the current task to mention the pre-commit failures and resolutions.

14. **Stage Changes (Again):**
    * If files were modified while fixing pre-commit issues, re-stage them.
    * Command: `git add .`

15. **Update Task List:**
    * Open the relevant `docs/todo/` file (e.g., `01-*.md`).
    * Locate the completed subtask and mark its main checkbox as done (e.g., change `[ ]` to `[x]`).
    * Stage this change: `git add docs/todo/<filename>.md`

16. **Commit Changes:**
    * Commit the staged changes with a clear and concise commit message following the project's conventions (e.g., `feat(scope): description`, `fix(scope): description`, `test(scope): description`).
    * Command: `git commit -m "type(scope): description"`
    * **Note:** Use `--no-verify` *only* if specifically agreed upon for known, temporary pre-commit failures that will be addressed in a subsequent task (e.g., unused imports for future functionality).

---
