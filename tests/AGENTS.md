# AGENTS.md — tests/

## Scope
Test suite. All code changes require tests. Coverage ≥ 90%.

## Validate
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```

## Layout
- `tests/unit/` for pure, fast tests.
- Optional live/e2e behind env flags.

## Conventions
- Use fixtures for setup.
- Mock HTTP at unit level.
- Assert types and values.
