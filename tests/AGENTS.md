# AGENTS.md — tests/

## Policy
All code changes require tests. Target coverage ≥ 90%.

## Layout
- `tests/unit/` for pure, fast tests.
- Optional live/e2e behind env flags.

## Conventions
- Use fixtures for setup.
- Mock HTTP at unit level.
- Assert types and values.

## Run
```bash
poetry run pytest -q
```
