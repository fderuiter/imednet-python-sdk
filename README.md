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
from imednet.utils import configure_json_logging

configure_json_logging()
sdk = ImednetSDK()
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

## Configuration

Set the following environment variables before using the SDK or CLI:

- `IMEDNET_API_KEY` – your API key
- `IMEDNET_SECURITY_KEY` – your security key
- `IMEDNET_BASE_URL` – optional base URL for private deployments

Additional variables such as `IMEDNET_STUDY_KEY` are used in the examples and
test suite. See `docs/test_skip_conditions.rst` for a full list.

## CLI Entry Points

The package installs an `imednet` command with subcommands for studies, sites,
subjects, records, jobs, queries and more. Use `imednet --help` to explore all
options.

## Testing & Development

```bash
./scripts/setup.sh  # once
poetry run ruff check --fix .
poetry run black --check .
poetry run mypy imednet
poetry run pytest -q
```

## Building & Publishing

```bash
python -m build
python -m twine upload dist/*
```

Pushing a Git tag like `v0.1.3` triggers the GitHub Actions workflow that builds
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

