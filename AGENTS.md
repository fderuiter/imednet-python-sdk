# AGENTS.md — Contributor Guide

## 1. Stack Identification

Before executing any task, audit the active dependency stack. Do not assume the presence of any library.

1. Parse `pyproject.toml` (`[tool.poetry.dependencies]` and `[tool.poetry.group.dev.dependencies]`) and `poetry.lock` to identify the exact versions in use.
2. Use only libraries already declared in those files. Never introduce a conflicting or unlisted package without an explicit instruction to update dependencies.
3. Apply the following decision matrix when selecting implementation patterns:

| Concern | Source of truth | Current library |
|---|---|---|
| HTTP client | `pyproject.toml` | `httpx` |
| Data validation / models | `pyproject.toml` | `pydantic` v2 |
| CLI framework | `pyproject.toml` | `typer[all]` |
| Retry logic | `pyproject.toml` | `tenacity` |
| HTTP mocking in tests | `pyproject.toml` (dev) | `respx` |
| Type checking | `pyproject.toml` (dev) | `mypy` |
| Linting | `pyproject.toml` (dev) | `ruff` |
| Formatting | `pyproject.toml` (dev) | `black`, `isort` |

## 2. Verification Loop

Before proposing any solution, execute and pass all CI quality gates locally.

1. Read `.github/workflows/main.yml` (the `quality` job) to identify the authoritative lint, format, and type-check commands.
2. Run the full gate in order:
   ```bash
   poetry run black --check .
   poetry run isort --check --profile black .
   poetry run ruff check .
   poetry run mypy src/imednet
   poetry run pytest -q --cov=imednet --cov-fail-under=90
   ```
3. Fix every reported error before marking a task complete. Re-run until the entire sequence exits 0.
4. Build documentation and confirm zero warnings:
   ```bash
   make docs
   ```

## 3. Architectural Separation of Concerns

### Data Layer (`src/imednet/models/`)
- Define all data schemas here as Pydantic v2 models.
- No business logic, no HTTP calls, no imports from `imednet.http` or `imednet.workflows`.
- Provide stable deserialization; field aliases are permitted, computed properties are not.

### Application Layer (`src/imednet/`)
| Sub-package | Responsibility | Rules |
|---|---|---|
| `src/imednet/http/` | Low-level HTTP transport | Retries (idempotent + jitter via `tenacity`), timeouts, rate-limit headers (`Retry-After`). Map status codes to `imednet.errors`. Redact secrets before logging. |
| `src/imednet/auth/` | Credential management | Never log or print tokens. Mask values in all representations. Thread- and async-safe. |
| `src/imednet/errors/` | Exception hierarchy | `ImednetError` → `AuthError`, `RateLimitError`, `ApiError`. No imports from sibling sub-packages. |
| `src/imednet/pagination/` | Cursor/page iteration | Lazy iteration, bounded memory. Expose page size and cursor. |
| `src/imednet/utils/` | Pure helpers | No side effects, no network I/O, no imports from `src/imednet/http/` or `src/imednet/workflows/`. |
| `src/imednet/workflows/` | Higher-level orchestration | Batching, retries, transforms. Inject client via constructor. Fail loudly with typed errors. |

New endpoints must be typed methods on the appropriate resource class. Shared logic belongs in `utils/`. Breaking API changes require a major version bump.

### Presentation Layer (`src/imednet/cli/`)
- The CLI handles argument parsing and terminal output **only**.
- No SDK logic, HTTP calls, or data transformation may reside in CLI modules.
- Log to stderr at INFO by default; support `--verbose` / `--quiet`.
- Every command must have complete `--help` text.
- Exit 0 on success, non-zero on any error.

## 4. Immutable Constraints

### Credential Handling
- **Never** log, print, write to disk, or transmit API keys, security keys, tokens, or authorization headers in plaintext under any circumstance.
- Mask credential values in all log output and exception messages.

### Testing Boundaries
| Test location | Network access | Required mock library |
|---|---|---|
| `tests/unit/` | Forbidden — no live requests | `respx` for `httpx`, `responses` for `requests` |
| `tests/integration/` | Forbidden — use recorded fixtures | `respx` / `responses` |
| `tests/live/` | Permitted — real API calls | None (guarded by `IMEDNET_RUN_E2E` env var) |

- All new or modified code must include or update tests in `tests/unit/`.
- Coverage must remain ≥ 90%.
- Do not add `tests/live/` calls to the default `pytest` run.

### Commit Messages and Pull Requests
- PR titles must follow Conventional Commits. Permitted prefixes: `feat:`, `fix:`, `chore:`, `docs:`, `ci:`, `test:`, `refactor:`, `perf:`, `revert:`. The `Semantic PR Title` CI check enforces this.
- Merge to `main` via **Squash and merge** so the PR title becomes the commit message.
- Changes that affect the public API, CLI interface, or environment variables must be noted in the PR description for Render deployment review.

### Release Process
- Do **not** manually edit `project.version` in `pyproject.toml`. Versions are managed automatically by `release-please`.
- Releases are triggered by merging the bot-created Release PR into `main`; publishing to PyPI is handled by the tag-triggered `publish` job in `.github/workflows/main.yml`.

## 5. Area Guidelines

### SDK Core (`src/imednet/`)
- **Change Policy**: New endpoints → typed methods. Shared logic → utilities. Breaking changes → major bump.
- **Scope**: Python 3.10–3.12. Work in `src/imednet/`, `tests/`, `docs/`, `examples/`, `scripts/`, `.github/`.

### Docs (`docs/`)
- **Tools**: Sphinx (`make docs`). Zero warnings.
- **Content**: Document every public API and CLI command. Sync README quickstart. Provide one runnable snippet per feature.

### Scripts & Examples
- **Scripts (`scripts/`)**: Dev tooling only. Scripts must be idempotent and begin with `set -euo pipefail`.
- **Examples (`examples/`)**: Runnable, minimal. Configure via environment variables. No hidden state.

### GitHub (`.github/`)
- **Workflows**: Mirror local quality gates. Release is automated via `release-please` on pushes to `main`.
- **PRs**: Title must match Conventional Commits format. All required status checks must be green before merge.
- **Issues**: Bug reports require reproduction steps and Python/library versions. Feature requests require a concrete use-case.

## 6. Setup

```bash
./scripts/setup.sh
```
