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
poetry run mypy packages/core/src/imednet
poetry run pytest -q
```
Coverage must stay ≥ 90%.

## HTTP transport mocking
- Use `respx` for tests that exercise `Client` or `AsyncClient` HTTP behavior.
- Do not patch `Client._client.request`, `AsyncClient._client.request`, or executor
  `send` callables just to intercept outbound `httpx` traffic.
- Prefer strict routers such as
  `@respx.mock(assert_all_called=True, assert_all_mocked=True)` so unmocked requests
  fail fast and unused routes are caught.
- Validate request construction inside the route handler when needed (for example,
  query parameters, dynamic URLs, and retry behavior).

## Package metadata and versioning
- The package metadata lives in `packages/*/pyproject.toml`.
- Never manually edit package versions in `packages/*/pyproject.toml`.

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
   poetry run mypy packages/core/src/imednet
   poetry run pytest -q
   ```
3. Merge to `main` using **Squash and merge** so the PR title becomes the merged commit message.
4. The `Automated Release` workflow runs `release-please` in manifest mode on `main` pushes and
   opens/updates a Release PR with calculated semantic version and changelog updates for the package
   manifests under `packages/`.
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

## Docstring standards

All public APIs must be documented using **Google-style docstrings** so that `sphinx.ext.napoleon`
can parse them correctly.

Key rules:

1. **Type hints belong in the function signature only.** Do not duplicate type information inside
   the docstring body.
2. **Google format sections** use four-space indentation and the exact keywords `Args:`, `Returns:`,
   `Raises:`, `Example:`, etc. Writing `Arguments:` or `Parameters:` instead of `Args:` will cause
   malformed output.
3. **Mypy compliance is a prerequisite for documentation.** `sphinx-autodoc-typehints` evaluates
   actual Python type annotations; broken or missing annotations will render incorrectly.
4. **Static `.rst` files are reserved for architectural overviews and tutorials only.**
   Do not create manually maintained `.rst` files for individual modules, classes, or CLI commands.
   API reference documentation is generated automatically by `sphinx-apidoc` into `docs/api/`
   (excluded from version control via `.gitignore`).

### Docstring example

```python
def fetch_records(study_key: str, page: int = 0) -> list[Record]:
    """Retrieve a page of records for the given study.

    Args:
        study_key: Unique identifier for the study.
        page: Zero-based page index.

    Returns:
        A list of Record objects for the requested page.

    Raises:
        ApiError: If the server returns a non-2xx status code.
    """
```

### Pre-merge documentation checklist

Before opening a pull request that adds or modifies public APIs:

1. Run `poetry run mypy packages/core/src/imednet` and confirm zero errors.
2. Run `make docs` locally. This command regenerates `docs/api/` via `sphinx-apidoc` and then
   compiles the HTML with `-W --keep-going`, treating every Sphinx warning as an error.
3. Open `docs/_build/html/index.html` and verify that type hints appear in the parameter
   descriptions with no raw reStructuredText syntax leaking into the rendered page.


## Pull requests
1. Fork the repository and create a feature branch.
2. Include validation output in the PR description.
3. Keep PRs scoped; one change per PR.
4. Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).
