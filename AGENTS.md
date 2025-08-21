# AGENTS.md — Contributor Guide

## Scope
Python 3.11–3.12. Work in `imednet/`, `imednet/workflows/`, `tests/`, `docs/`,
`examples/`, `scripts/`, `.github/`.

## Validate
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```
Coverage ≥ 90%.

## Contribute
DRY + SOLID. Line length 100. Conventional Commits. Update `[Unreleased]` in
`CHANGELOG.md`.

* Read nearby code, tests, and docs first.
* Add or update tests with any code change.
* Update docs and an example for any public API or CLI change.
* In PR, include paths changed and validation output.

## Setup
```bash
./scripts/setup.sh
```

## Release
1. Update CHANGELOG.
2. `poetry version <bump>`
3. `make docs`
4. Commit + tag `vX.Y.Z`
5. Push branch + tag to publish.
