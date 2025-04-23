# imednet-python-sdk

[![Build Status](https://github.com/FrederickdeRuiter/imednet-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/fderuiter/imednet-python-sdk/actions/workflows/ci.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imednet-python-sdk)](https://pypi.org/project/imednet-python-sdk/)

A Python SDK for interacting with the iMedNet REST API. Provides client, endpoint wrappers, and data models for all resources.

## Features

- Simple, consistent interface for API calls
- Automatic pagination
- Data models for requests and responses
- Workflow utilities for data extraction and mapping

## Installation

```bash
pip install imednet-python-sdk
```

Or install from source:

```bash
git clone https://github.com/fderuiter/imednet-python-sdk.git
cd imednet-python-sdk
poetry install --with dev
```

## Usage

```python
from imednet import SDK

client = SDK(api_key="YOUR_API_KEY")
studies = client.studies.get_all()
for study in studies:
    print(study.id, study.name)
```

See the full API reference in [docs/reference](docs/reference).

## Development

- Code style: [Black](https://github.com/psf/black), [ruff](https://github.com/charliermarsh/ruff), [mypy](http://mypy-lang.org/)
- Testing: [pytest](https://pytest.org/)

Build and test:

```bash
poetry run pytest --cov=imednet
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
