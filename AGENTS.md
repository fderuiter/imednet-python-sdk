# AGENTS.md — Contributor Guide

## Scope
Python 3.10–3.12. Work in `imednet/`, `tests/`, `docs/`, `examples/`, `scripts/`, `.github/`.

## Validate
Run these commands locally before pushing:
```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy imednet
poetry run pytest -q
```
Coverage ≥ 90%. Max line length 100.

## Setup
```bash
./scripts/setup.sh
```

## Release
1. `poetry version <bump>`
2. `make docs`
3. Commit + tag `vX.Y.Z`
4. Push branch + tag to publish.

## Area Guidelines

### SDK Core (`imednet/`)
- **Change Policy**: New endpoints → typed methods. Shared logic → utilities. Breaking changes → major bump.
- **Models (`imednet/models`)**: Pydantic models. Stable deserialization. No business logic.
- **HTTP (`imednet/http`)**: Handle retries (idempotent + jitter), timeouts, rate limits (Retry-After). Map errors to `imednet/errors`. Redact secrets in logs.
- **Auth (`imednet/auth`)**: Never log secrets. Mask tokens. Thread/async-safe.
- **Errors (`imednet/errors`)**: Hierarchy: `ImednetError` > `AuthError`, `RateLimitError`, `ApiError`.
- **Pagination (`imednet/pagination`)**: Lazy iteration. Bounded memory. Expose page size/cursor.
- **Utils (`imednet/utils`)**: Pure helpers. No cycles. High coverage.

### CLI (`imednet/cli`)
- **Design**: Stable interface. Typer/argparse. Pure I/O at edges. Business logic in SDK.
- **UX**: Complete `--help`. Log to stderr (INFO default). Support `--verbose`/`--quiet`.
- **Exit Codes**: 0 success, non-zero for error.

### Workflows (`imednet/workflows`)
- **Scope**: Higher-level orchestration (batching, retries, transforms).
- **Design**: Fail loud with custom errors. Inject client. Avoid hard-coded paths.

### Tests (`tests/`)
- **Layout**: `tests/unit/` for fast tests (mock HTTP). Optional live tests.
- **Policy**: All changes require tests.

### Docs (`docs/`)
- **Tools**: Sphinx (`make docs`). Zero warnings.
- **Content**: Document public API/CLI. Sync README quickstart. One runnable snippet per feature.

### Scripts & Examples
- **Scripts (`scripts/`)**: Dev tooling. Idempotent. `set -euo pipefail`.
- **Examples (`examples/`)**: Runnable, minimal. Config via env vars. No hidden state.

### GitHub (`.github/`)
- **Workflows**: Mirror local checks. Release on tag `vX.Y.Z`.
- **PRs**: Title `[<area>] <summary>`. Require green checks.
- **Issues**: Bugs need repro/versions. Features need use-case.
