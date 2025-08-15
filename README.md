# imednet

Unofficial Python SDK for the iMednet clinical trials API.

[![PyPI](https://img.shields.io/pypi/v/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/imednet.svg)](https://pypi.org/project/imednet/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imednet.svg)](https://pypi.org/project/imednet/)
[![License](https://img.shields.io/pypi/l/imednet.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/fderuiter/imednet-python-sdk/ci.yml?branch=main)](https://github.com/fderuiter/imednet-python-sdk/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](https://github.com/fderuiter/imednet-python-sdk)

## Purpose

This package simplifies integration with the iMednet REST API for clinical trial
management. It provides typed endpoint wrappers, helper workflows and a CLI so
researchers and developers can automate data extraction and submission without
reimplementing HTTP logic.

## Features

- Simple, consistent interface for API calls
- Automatic pagination across endpoints
- Pydantic models for requests and responses
- Workflow helpers for data extraction and mapping
- Pandas and CSV utilities
- Optional in-memory caching of study metadata
- Structured JSON logging and OpenTelemetry tracing
- Async client and command line interface

## Quickstart Installation

```bash
# PyPI release
pip install imednet
# Dev version
pip install git+https://github.com/fderuiter/imednet-python-sdk.git@main
```

## Minimal Example

```python
from imednet import ImednetSDK
from imednet.config import load_config
from imednet.utils import configure_json_logging

configure_json_logging()
cfg = load_config()
sdk = ImednetSDK(
    api_key=cfg.api_key,
    security_key=cfg.security_key,
    base_url=cfg.base_url,
)
print(sdk.studies.list())
```

## Tech Stack

- Python 3.10–3.12
- requests, httpx, pydantic, typer, tenacity, python-dotenv

## Project Structure

```
.
├── docs/       - Sphinx documentation
├── examples/   - Usage samples
├── imednet/    - SDK package
├── scripts/    - Helper scripts
└── tests/      - Unit and integration tests
```

## API Documentation

Full documentation is available at
<https://fderuiter.github.io/imednet-python-sdk/>.
The official iMednet API documentation is at <https://portal.prod.imednetapi.com/>.

## Postman Collection

The repository includes a ready-to-import Postman collection generated from
[`openapi.yaml`](openapi.yaml). Download
[`imednet.postman_collection.json`](imednet.postman_collection.json) and import it
into Postman to explore and test the API endpoints. The collection uses the
`{{baseUrl}}` variable for the API host; set this alongside your `x-api-key` and
`x-imn-security-key` headers in a Postman environment before sending requests.

## Configuration

The SDK and CLI read credentials from environment variables such as
`IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY`. See
[configuration](docs/configuration.rst) for the complete list, optional
settings, and `.env` support. Use `imednet.config.load_config()` to access these
values in your code.

## CLI Entry Points

The package installs an `imednet` command with subcommands for studies, sites,
subjects, records, jobs, queries and more. Use `imednet --help` to explore all
options.

Example of exporting a subset of variables:

```bash
imednet export sql MY_STUDY table sqlite:///data.db --vars AGE,SEX --forms 10,20
```

### SQLite exports

When the connection string uses SQLite, the command splits the output into one
table per form to avoid the 2000 column limit. Pass ``--single-table`` to
disable this behaviour. See ``docs/cli.rst`` for full examples.

## Testing & Development

```bash
./scripts/setup.sh  # once
poetry run ruff check --fix .
poetry run black --check .
poetry run mypy imednet
poetry run pytest -q
```

### Smoke-test workflow

The optional [smoke.yml](.github/workflows/smoke.yml) action runs the `tests/live` suite.
It relies on repository secrets `APIKEY` and `SECURITYKEY` and sets `IMEDNET_RUN_E2E`.
Use the workflow to confirm real API access on demand or via its nightly schedule.
INFO-level log messages stream to the terminal during these runs, making it easier to
debug failures.

## Building & Publishing

```bash
python -m build
python -m twine upload dist/*
```

Pushing a Git tag like `v0.1.4` triggers the GitHub Actions workflow that builds
and publishes the package to PyPI.

## Versioning & Changelog

This project follows [Semantic Versioning](https://semver.org). See
[CHANGELOG.md](CHANGELOG.md) for release history.

## Contributing

Contributions are welcome! Please read
[CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT license. See [LICENSE](LICENSE) for
details.

## Acknowledgements

Built with open source libraries including requests, httpx, pydantic and typer.

