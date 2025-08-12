# AGENTS.md — imednet/workflows/

## Scope
Higher-level orchestration over SDK: batching, pagination, retries, transforms.

## Guardrails
- Fail loud with clear custom errors; preserve server payloads.
- Keep I/O pluggable via interfaces; avoid hard-coded paths.
- No hidden network calls; accept an injected client.

## Validate
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```
Coverage ≥ 90%.

## Tests
Unit tests cover success and error paths.

## Docs
Each multi-step job needs a short how-to page with a runnable snippet and an
example under `examples/`.
