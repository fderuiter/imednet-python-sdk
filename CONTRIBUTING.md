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
poetry run mypy imednet
poetry run pytest -q
```
Coverage must stay ≥ 90%.

## Conventions
- DRY + SOLID. Line length 100.
- Use Conventional Commits.
- Add tests, docs, and examples for any public change.

## Pull requests
1. Fork the repository and create a feature branch.
2. Include validation output in the PR description.
3. Keep PRs scoped; one change per PR.
4. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

