# AGENTS Instructions for Codex

This repository uses pre-commit, pytest, and Sphinx. When changing files, run the following before committing:

1. **Run Pre-commit**
   ```bash
   pre-commit run --files <changed files>
   ```
   This executes `black`, `ruff`, and `mypy`. Fix any issues reported.

2. **Run Tests**
   ```bash
   pytest -q --cov=imednet
   ```
   All tests must pass.

3. **Build Docs** (when `docs/` files change)
   ```bash
   sphinx-build -b html docs docs/_build/html
   ```

4. **Commit Messages**
   - Use Conventional Commits (e.g., `feat:`, `fix:`).

5. **Environment Setup**
   - Install dependencies with `poetry install --with dev`.

6. **Project Layout**
   - Source code is in `imednet/`.
   - Tests are in `tests/`.
   - Line length is 100.
   - Do **not** commit generated artifacts such as `docs/_build/`.

7. **Testing Expectations**
   - Ensure new code paths are tested, referencing `tests/TEST_PLAN.md`.

