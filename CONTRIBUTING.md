# Contributing to iMednet Python SDK

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the codebase
- Submitting a fix or new feature

## How to Contribute

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature` or `git checkout -b fix/my-bug`.
3. Write tests for your change (`pytest`).
4. Ensure code style with `black`, `ruff`, and type checks with `mypy`.
5. Commit your changes following Conventional Commits:
   - `feat: add new endpoint for X`
   - `fix: correct pagination logic`
6. Push to your fork: `git push origin feature/my-feature`.
7. Open a Pull Request.

Please adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and provide:

- Version of the SDK
- Python version
- Steps to reproduce
- Expected vs actual behavior

## Suggesting Enhancements

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

## Style Guides

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use `black` for formatting.
- No trailing whitespace.

## Documentation

Documentation is built locally using Sphinx. There is no longer a CI workflow for automatic documentation deployment. To build the docs, run:

```bash
./scripts/setup.sh
poetry run sphinx-build -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` in your browser to view the documentation.

## Tests

Run tests locally:

```bash
poetry run pytest
```

Run `./scripts/setup.sh` before running tests to ensure all development
dependencies are installed and pre-commit hooks are set up.
