# AGENTS.md — imednet/ (SDK core)

## Purpose
Core HTTP clients, models, and CLI entry points. Keep the public surface stable.

## What to change
- Add endpoints as new client methods with typed params and returns.
- Keep side effects minimal; prefer pure helpers.
- Maintain backward compatibility; gate breaking changes behind a major bump.

## Required checks (run from repo root)
See root AGENTS.md “How to validate changes”. Add or update unit tests in `tests/`.

## Patterns
- Input/output models: Pydantic.
- Retries/timeouts: centralize in client config.
- Pagination helpers: reuse shared utilities.
- Logging: structured JSON; preserve request IDs if present.

## When docs are required
- New public method or CLI flag → docstring + docs page section + example.
