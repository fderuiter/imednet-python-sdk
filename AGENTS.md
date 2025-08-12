# AGENTS.md — Contributor Guide

## Scope and map
Work mainly in:
- `imednet/` — SDK modules, CLI entry point, async client
- `imednet/workflows/` — higher-level workflow utilities
- `tests/` — pytest suite and fixtures
- `docs/` — Sphinx docs site
- `examples/` — runnable usage samples

## Style and contribution rules
- Follow DRY and SOLID. Prefer small, focused abstractions.
- Max line length: 100 chars.
- Use Conventional Commits.
- Update `CHANGELOG.md` under `[Unreleased]` for every change.

## Dev environment
- One-time setup: `./scripts/setup.sh`
- Python 3.10–3.12 supported.
- Use Poetry for deps. Use pre-commit hooks.

## How to validate changes
Run before any commit:
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```

All checks must pass. Coverage target ≥ 90%.

## How to work as an “agent”

When adding or changing code:

1. Read related modules under `imednet/` and any sibling workflow or model files.
2. Scan `tests/` for existing cases and fixtures; add or update tests with your change.
3. If the public API or CLI changes, update `docs/` and an example under `examples/`.
4. Produce a PR with:

   * Title: `[imednet] <short change>` or `[workflows] <short change>`
   * Summary: what changed and why
   * Affected paths
   * Validation: paste local check outputs (ruff/black/mypy/pytest) and coverage
   * Changelog entry

## Docs

* Build locally: `make docs`
* Ensure new public APIs have minimal docstrings and a docs page or section.

## Release process

1. Update `CHANGELOG.md`.
2. `poetry version <bump>`
3. `make docs`
4. Commit + tag `vX.Y.Z`
5. Push branch and tag to trigger release workflow to PyPI.

## Where to look for context

* `README.md` for project overview and commands
* `CONTRIBUTING.md` for broader guidelines
* `tests/` for usage and behaviors
* `docs/` for CLI and API docs

