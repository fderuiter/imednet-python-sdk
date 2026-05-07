# Contributing

## Project scope
The SDK targets Python 3.10–3.12 and includes:

- Core client and models under `imednet/`
- Workflows in `imednet/workflows/`
- Docs, tests, examples, and tooling in their directories

## Prerequisites
- [Poetry](https://python-poetry.org/docs/) (for dependency management)
- [Make](https://www.gnu.org/software/make/) (optional, for building docs)

## Setup
```bash
./scripts/setup.sh
```

## Validation
Run before committing:

```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run isort --check --profile black .
poetry run mypy src/imednet
poetry run pytest -q
```
Coverage must stay ≥ 90%.

## Package metadata and versioning
- The `[project]` block in `pyproject.toml` is the single source of truth for package metadata.
- Never manually edit `project.version` in `pyproject.toml`.

## Release workflow
Releases are fully automated and driven by merged PR titles:

1. Ensure your PR title follows Conventional Commits. Supported prefixes are `feat:`, `fix:`,
   `chore:`, `docs:`, `ci:`, `test:`, `refactor:`, `perf:`, and `revert:`. The CI
   `Semantic PR Title` check enforces this.
2. Ensure your branch is up to date and all validation checks pass:
   ```bash
   poetry run ruff check --fix .
   poetry run black --check .
   poetry run isort --check --profile black .
   poetry run mypy src/imednet
   poetry run pytest -q
   ```
3. Merge to `main` using **Squash and merge** so the PR title becomes the merged commit message.
4. The `Automated Release` workflow runs `release-please` on `main` pushes and opens/updates a
   Release PR with calculated semantic version, changelog updates, and `pyproject.toml` version
   updates.
5. Maintainers trigger publication by approving and merging the bot-created Release PR.

Configuration requirements:
- Publishing requires `PYPI_API_TOKEN` in repository secrets (or migration to PyPI Trusted
  Publishers/OIDC).
- Configure branch protection on `main` to require pull request reviews and required status checks,
  including `Semantic PR Title`.

## Conventions
- DRY + SOLID. Line length 100.
- Use Conventional Commit prefixes in PR titles (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`,
  `test:`, `refactor:`, `perf:`, `revert:`).
- Add tests, docs, and examples for any public change.

## Pull requests
1. Fork the repository and create a feature branch.
2. Include validation output in the PR description.
3. Keep PRs scoped; one change per PR.
4. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).
