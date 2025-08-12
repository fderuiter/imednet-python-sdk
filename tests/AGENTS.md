# AGENTS.md — tests/

## Policy
- Tests are required for all changes. Aim for coverage ≥ 90%.
- Prefer small, focused tests; use fixtures for setup.

## Layout
- `tests/unit/` for pure units
- `tests/live/` optional smoke/e2e gated by env vars

## Running
```bash
poetry run pytest -q
```

## Writing tests

* Assert types and values.
* For network calls, mock HTTP at unit level; allow optional live runs via flags/env.
