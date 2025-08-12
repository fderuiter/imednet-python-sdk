# AGENTS.md — Contributor Guide

## Where to work
`imednet/`, `imednet/workflows/`, `tests/`, `docs/`, `examples/`, `scripts/`, `.github/`.

## Style
DRY + SOLID. Line length 100. Conventional Commits. Update `[Unreleased]` in `CHANGELOG.md`.

## One-time
```bash
./scripts/setup.sh
```

## Validate before commit

```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```

Coverage ≥ 90%.

## How agents should work

* Read nearby code, tests, and docs first.
* Add or update tests with any code change.
* Update docs and an example for any public API or CLI change.
* In PR, include paths changed and validation output.

## Release

1. Update CHANGELOG.
2. `poetry version <bump>`
3. `make docs`
4. Commit + tag `vX.Y.Z`
5. Push branch + tag to publish.
