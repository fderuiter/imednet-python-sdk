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
- Update `CHANGELOG.md` manually. Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) style and
  [semantic versioning](https://semver.org/).
- Summarize each commit under the `Unreleased` section. When releasing, move
  these entries under a new version heading.

