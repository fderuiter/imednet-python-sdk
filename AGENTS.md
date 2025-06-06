# Guidelines for Contributors

## Environment Setup
- Use Python 3.12 with [Poetry](https://python-poetry.org/).
- Install dependencies including development extras:
  ```bash
  poetry install --with dev
  ```
- Run `./scripts/setup.sh` once to configure pre-commit hooks.

## Style and Static Analysis
- Format code with [Black](https://github.com/psf/black) using a line length of 100.
- Lint with [ruff](https://github.com/astral-sh/ruff).
- Type‑check with [mypy](http://mypy-lang.org/).
- These checks are executed via pre-commit. Run them once on the entire
  repository and on the files you change before every commit:
  ```bash
  # first run on all files
  poetry run pre-commit run --all-files
  # then run on the specific files you changed
  poetry run pre-commit run --files <files you changed>
  ```

## Design Principles
- **Single Responsibility** – Keep each module or class focused on one concern. Prefer
  composition over long multi-purpose classes.
- **Open/Closed and Liskov** – Extend functionality with new subclasses or helper
  functions without altering existing interfaces.
- **Interface Segregation** – Expose small, well-defined interfaces instead of large
  "god objects."
- **Dependency Injection** – Pass dependencies into classes and functions rather
  than instantiating them internally. This aids testing and reuse.
- **DRY** – Reuse utilities and base classes. Factor shared routines into
  `imednet.utils` or `core`.
- **Testability** – Keep modules decoupled so they can be tested independently. Add
  unit tests with new classes or functions.

## Testing
- Run the test suite with coverage:
  ```bash
  poetry run pytest --cov=imednet
  ```
- Pull requests should not lower overall coverage.

## Changelog
- Update `CHANGELOG.md` manually. Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) style and
  [semantic versioning](https://semver.org/).
- Summarize each commit under the `Unreleased` section. When releasing, move
  these entries under a new version heading.

