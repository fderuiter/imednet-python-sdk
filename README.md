# imednet-python-sdk

[![Build Status](https://github.com/Bright-Research/imednet-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/Bright-Research/imednet-python-sdk/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Bright-Research/imednet-python-sdk/graph/badge.svg?token=YOUR_CODECOV_TOKEN_HERE)](https://codecov.io/gh/Bright-Research/imednet-python-sdk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imednet-python-sdk)](https://pypi.org/project/imednet-python-sdk/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

A Python SDK for interacting with the iMedNet REST API. Provides client, endpoint wrappers, and data models for all resources.

See the [Changelog](CHANGELOG.md) for release history.

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
git clone https://github.com/Bright-Research/imednet-python-sdk.git
cd imednet-python-sdk
poetry install --with dev
```

## Usage

First, ensure you have set your iMedNet API credentials as environment variables:

```powershell
# For PowerShell:
$env:IMEDNET_API_KEY="your_api_key_here"
$env:IMEDNET_SECURITY_KEY="your_security_key_here"
# Optional: Set if using a non-standard base URL
# $env:IMEDNET_BASE_URL="https://your.imednet.instance/api"

# For Bash/Zsh:
# export IMEDNET_API_KEY="your_api_key_here"
# export IMEDNET_SECURITY_KEY="your_security_key_here"
# export IMEDNET_BASE_URL="https://your.imednet.instance/api"
```

### Using the Python SDK

Then, you can use the SDK like this:

```python
import os
from imednet.sdk import ImednetSDK as ImednetClient

# Credentials are read automatically from environment variables
api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
base_url = os.getenv("IMEDNET_BASE_URL") # Optional

try:
    client = ImednetClient(api_key=api_key, security_key=security_key, base_url=base_url)
    
    # Example: List the first 5 studies
    studies = client.studies.list()
    print("Studies found:")
    for study in studies[:5]: # Limit to first 5 for brevity
        print(f"- Name: {study.study_name}, Key: {study.study_key}")

except Exception as e:
    print(f"Error: {e}")
```

### Using the Command Line Interface (CLI)

After installing the package (`pip install imednet-python-sdk`) and setting the environment variables as shown above, you can use the `imednet` command:

```powershell
# List available studies
imednet studies list

# List sites for a specific study (replace STUDY_KEY)
imednet sites list STUDY_KEY

# List subjects for a specific study, filtering by status (replace STUDY_KEY)
imednet subjects list STUDY_KEY --filter "subject_status=Screened"

# Get help for a specific command
imednet subjects list --help 
```

- See the full API reference in the [HTML docs](docs/_build/html/index.html).
- More examples can be found in the `imednet/examples/` directory.

## Documentation

The full documentation is generated with Sphinx and output to `docs/_build/html`.
To build it locally:

```bash
poetry install --with dev
poetry run sphinx-build -b html docs docs/_build/html
```

Then open `docs/_build/html/index.html` in your browser.

## Development

- Code style: [Black](https://github.com/psf/black), [ruff](https://github.com/charliermarsh/ruff), [mypy](http://mypy-lang.org/)
- Testing: [pytest](https://pytest.org/)

Build and test:

```bash
poetry run pytest --cov=imednet
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Governance and Roadmap

This project is currently maintained by Bright Research. We welcome contributions!

*(Optional: Add details about project governance, decision-making processes, and future development plans or roadmap here.)*

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
