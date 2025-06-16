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

### Coding Principles
Keep the implementation DRY and apply the SOLID principles:

- **DRY** – eliminate repetition by refactoring shared logic into reusable
  functions or classes.
- **Single Responsibility** – each module or class should focus on one thing
  and do it well.
- **Open/Closed** – extend behavior with new components instead of modifying
  existing ones.
- **Liskov Substitution** – design abstractions so derived types can replace
  their base without side effects.
- **Interface Segregation** – expose small, focused interfaces over large
  monolithic ones.
- **Dependency Inversion** – depend on abstractions rather than concrete
  implementations to encourage loose coupling.

Following these guidelines keeps the SDK maintainable and extensible.

## Codebase Overview
- `imednet/` contains the SDK modules, CLI entry point, and async client.
- `imednet/workflows/` holds higher level workflow utilities.
- `tests/` provides the pytest suite used in CI.
- Documentation can be built locally via `make docs`.

Follow the guidelines in `CONTRIBUTING.md` and use Conventional Commits for commit messages.
Record your changes in `CHANGELOG.md` under the `[Unreleased]` section.
