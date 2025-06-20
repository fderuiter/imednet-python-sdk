# imednet-python-sdk

\
[![Build Status](https://github.com/Bright-Research/imednet-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/Bright-Research/imednet-python-sdk/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/imednet-python-sdk.svg)](https://pypi.org/project/imednet-python-sdk/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/imednet-python-sdk)](https://pypi.org/project/imednet-python-sdk/)
[![PyPI license](https://img.shields.io/pypi/l/imednet-python-sdk.svg)](LICENSE)
[![PyPI downloads](https://img.shields.io/pypi/dm/imednet-python-sdk.svg)](https://pypi.org/project/imednet-python-sdk/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
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
import json
from imednet.sdk import ImednetSDK
from imednet.workflows.study_structure import get_study_structure

# Set your credentials and study key (or use environment variables)
api_key = os.getenv("IMEDNET_API_KEY")
security_key = os.getenv("IMEDNET_SECURITY_KEY")
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
base_url = os.getenv("IMEDNET_BASE_URL")  # Optional

sdk = ImednetSDK(api_key=api_key, security_key=security_key, base_url=base_url)

try:
    structure = get_study_structure(sdk, study_key)
    print("Study structure loaded:")
    print(json.dumps(structure.model_dump(by_alias=True), indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f"Error retrieving study structure: {e}")
```

### Using the Command Line Interface (CLI)

After installing the package (`pip install imednet-python-sdk`) and setting the environment variables as shown above, first verify the CLI is available by running `imednet --help`. You can then use the `imednet` command:

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

The documentation is no longer automatically deployed or published online. To
view the documentation, you must build it locally using Sphinx. The output will
be in `docs/_build/html`.

You can build the docs using the included Makefile target:

```bash
make docs
```

This installs the development dependencies and runs the Sphinx build. If you
prefer, you can run the commands manually:

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

This project is currently maintained by Bright Research.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
