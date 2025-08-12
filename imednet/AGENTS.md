# AGENTS.md — imednet/ (SDK core)

## Purpose
Core client, models, and CLI. Keep public API stable.

## Edit here
- New endpoints → typed client methods + small helpers.
- Shared logic → utilities, not copy-paste.
- Breaking changes → major bump only.

## Required checks (run at repo root)
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```

Coverage ≥ 90%. Max line length 100.

## Context to read first

`README.md`, `CONTRIBUTING.md`, `tests/`, `docs/`.

## PR checklist

* Scope: `[imednet] ...`
* API surface documented (docstrings + docs page).
* Tests added/updated.
* Changelog updated under `[Unreleased]`.
