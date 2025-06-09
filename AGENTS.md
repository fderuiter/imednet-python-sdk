# AGENTS Instructions for Codex

This repository uses Poetry, pre-commit, pytest and Sphinx. Follow these steps when updating the project.

## Environment Setup
- Install dependencies with `poetry install --with dev`.

## Workflow
1. **Formatting and Static Analysis**
   ```bash
   pre-commit run --files <changed files>
   ```
   This runs `black`, `ruff` and `mypy` with a line length of 100. Fix any issues.

2. **Run Tests**
   ```bash
   pytest -q --cov=imednet
   ```
   All tests must pass.

3. **Build Documentation** (when files under `docs/` change)
   ```bash
   sphinx-build -b html docs docs/_build/html
   ```

4. **Commit Messages**
   - Use Conventional Commit style (`feat:`, `fix:`, `docs:`, `chore:`).
   - Keep the subject line under 72 characters.

## General Guidelines
- Source code resides in `imednet/`.
- Tests reside in `tests/`.
- Do **not** commit generated artifacts such as `docs/_build/`.
- Ensure new functionality is covered by tests and maintain high coverage.
- Update `CHANGELOG.md` and documentation when user facing changes are made.
