# Guidelines for Contributors

## Environment Setup
- Use Python 3.10 with [Poetry](https://python-poetry.org/).
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

## Testing
- Run the test suite with coverage:
  ```bash
  poetry run pytest --cov=imednet
  ```
- Pull requests should not lower overall coverage.

## Changelog
- The changelog is updated automatically using `scripts/update_changelog.py`.
  Run the script before releasing to append recent commits to the
  `Unreleased` section:
  ```bash
  poetry run python scripts/update_changelog.py
  ```

