# AGENTS.md — .github/

## Workflows
- Tests and checks must mirror local commands:
  - ruff, black, isort, mypy, pytest, coverage gate ≥ 90%.
- Release pipeline:
  - Tag `vX.Y.Z` triggers `.github/workflows/release.yml` to `poetry build`
    and publish via `pypa/gh-action-pypi-publish`.

## PR hygiene
- Title: `[<area>] <summary>`
- Require green checks before merge.
- Block direct pushes to default branch.

## Bot outputs
- Keep annotations terse. Fail fast on formatting and types.
