# Pre-Commit Velocity and Quality Tiering

## Context and Decision

The repository initially attempted to run a comprehensive multi-tool gate (`hatch run lint:all`) directly inside pre-commit hooks, bundling 10 static, security, and type-checking tools—including whole-codebase type resolution (`mypy`), AST similarity analysis (`pylint`), and network-bound CVE lookups (`pip-audit`). This imposed significant friction on developer velocity (30–90 seconds per local commit) and broke environments lacking a global `hatch` installation.

We decided to establish a strict two-tiered quality strategy:
1. **Tier 1 (`pre-commit` stage)**: Constrained to sub-second, staged-file operations running via native Python `pre-commit` (`ruff format`, `ruff --fix`, `typos`, `detect-secrets`, git hygiene checks, and root sanitization).
2. **Tier 2 (Pre-PR Verification & CI)**: Heavy, full-workspace checks (`mypy`, strict coverage testing via `pytest`, `vulture`, `pylint-sim`, `semgrep`, `pip-audit`, and documentation building) are executed through the authoritative verification loop (`docs/how-to/verification.rst`) and enforced on GitHub Actions CI.

## Considered Options

- **Option A (Husky + lint-staged)**: Introduces Node.js and npm package-lock overhead to an otherwise pure Python monorepo. Rejected to preserve a unified Python tooling stack.
- **Option B (Heavy commit-time linting)**: Full static analysis and vulnerability scanning on every git commit. Rejected because network timeouts and 90s commit latency compromise developer velocity and encourage `--no-verify` circumvention.
- **Option C (Lightweight staged pre-commit hooks + full CI quality gate)**: Accepted. Commits execute in <1.5s while preventing credential leaks, syntax errors, and style regressions before code is pushed.

## Consequences

- Commits are instantaneous and safe against common regressions (formatting errors, trailing whitespace, committed secrets, unapproved root files).
- Developers must execute the local verification loop (`docs/how-to/verification.rst`) prior to opening pull requests, as deep semantic errors and test failures are guarded at PR/CI boundaries rather than local commit boundaries.
