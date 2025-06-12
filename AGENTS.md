# Development Guide

This repository uses `poetry` for dependency management and `pre-commit` for formatting and linting.
Run `./scripts/setup.sh` once to install the development packages and set up the pre-commit hooks.
## Required Checks
Run the following commands before committing any code:

```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run mypy imednet
poetry run pytest -q
```

All checks must pass. The project enforces a maximum line length of 100 characters.

## Codebase Overview
- `imednet/` contains the SDK modules, CLI entry point, and async client.
- `imednet/workflows/` holds higher level workflow utilities.
- `tests/` provides the pytest suite used in CI.
- Documentation can be built locally via `make docs`.

Follow the guidelines in `CONTRIBUTING.md` and use Conventional Commits for
commit messages.
