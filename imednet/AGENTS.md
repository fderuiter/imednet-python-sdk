# AGENTS.md — imednet/ (SDK core)

## Scope
Core client, models, and CLI. Keep the public API stable.

## Change policy
- New endpoints → typed client methods with small helpers.
- Shared logic → utilities, not copy-paste.
- Breaking changes → major bump only.

## Validate
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```
Coverage ≥ 90%. Max line length 100.

## Docs
Document any public surface (docstrings + docs page) and update examples.

## PR checklist
- Scope: `[imednet] ...`
- Tests added/updated.
- Docs updated.
- Changelog entry under `[Unreleased]`.
