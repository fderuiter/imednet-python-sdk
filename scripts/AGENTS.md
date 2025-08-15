# AGENTS.md — scripts/

## Scope
Developer tooling only.

## Standard script
- `setup.sh` installs dev deps and pre-commit.
- New scripts must be idempotent and `set -euo pipefail`.

## Expectations
- Document usage with `-h` or a top comment.
- No hard-coded local paths.
- Keep shellcheck clean.

## Run in CI?
If a script is required by CI, pin its interface and avoid breaking changes.
