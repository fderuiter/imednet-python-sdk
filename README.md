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
- Pandas helpers for DataFrame conversion and CSV export
- Optional in-memory caching for study and variable listings

Calls to `sdk.studies.list()` and `sdk.variables.list()` cache results in memory.
Use `refresh=True` to fetch fresh data.

## Installation

```bash
pip install imednet-python-sdk
```

Or install from source:

```bash
git clone https://github.com/Bright-Research/imednet-python-sdk.git
cd imednet-python-sdk
./scripts/setup.sh
```

## Usage

First, ensure you have set your iMedNet API credentials as environment variables.
Keep these keys secure and never commit them to source control:

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

# Credentials are automatically read from the IMEDNET_API_KEY and
# IMEDNET_SECURITY_KEY environment variables.
study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")

sdk = ImednetSDK()  # uses environment variables for authentication

try:
    structure = get_study_structure(sdk, study_key)
    print("Study structure loaded:")
## JSON Logging and Tracing

The SDK can emit structured JSON logs for each HTTP request. Call `configure_json_logging()` before creating a client and control the log level with the `log_level` parameter.

```python
from imednet.utils import configure_json_logging
from imednet.core.client import Client

configure_json_logging()
client = Client(api_key="...", security_key="...", log_level="INFO")
```

If `opentelemetry` is installed, you can pass a tracer instance or rely on the global provider. Each request is wrapped in a span with attributes for the endpoint path and status code. Installing `opentelemetry-instrumentation-requests` enables automatic propagation of trace context.

    print(json.dumps(structure.model_dump(by_alias=True), indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f"Error retrieving study structure: {e}")
```
### Async Usage

Use `AsyncImednetSDK` when working with asyncio:

```python
import os
from imednet.async_sdk import AsyncImednetSDK

async def main():
    study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
    async with AsyncImednetSDK() as sdk:
        studies = await sdk.studies.async_list()
        print(studies)

# asyncio.run(main())
```


### Record Validation

The SDK can validate record payloads locally using cached form metadata. Create
a :class:`~imednet.utils.schema.SchemaCache` and pass it to
``RecordsEndpoint.create`` or the ``RecordUpdateWorkflow`` methods. A
``ValidationError`` is raised if variables are unknown or required fields are
missing.

```python
from imednet.utils.schema import SchemaCache

schema = SchemaCache()
schema.refresh(sdk.forms, sdk.variables, study_key)
sdk.records.create(study_key, record_data, schema=schema)
```

### Exporting records to CSV

Install the optional pandas dependency and call
``export_records_csv`` to save all records for a study:

```bash
pip install imednet-python-sdk[pandas]
```

```python
from imednet.utils.pandas import export_records_csv

sdk = ImednetSDK()
export_records_csv(sdk, study_key, "records.csv")
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

# List records for a specific study and save as CSV
imednet records list STUDY_KEY --output csv

# Save records as JSON
imednet records list STUDY_KEY --output json

# Omit --output to print a table preview
imednet records list STUDY_KEY

# Get help for a specific command
imednet subjects list --help
```

- See the full API reference in the [HTML docs](docs/_build/html/index.html).
- More examples can be found in the `imednet/examples/` directory.

### JSON Logging

All logs from the SDK use JSON format so they can be easily parsed. Pass `log_level`
 to `imednet.core.client.Client` to adjust verbosity. Call
 `imednet.utils.configure_json_logging()` if you want to enable the same formatting
 for your entire application.


### Tracing with OpenTelemetry

The SDK can emit OpenTelemetry spans for each HTTP request.
Install `opentelemetry-instrumentation-requests`
automatically instrument the underlying HTTP calls,
or provide your own tracer to `imednet.core.client.Client`.


### Tracing with OpenTelemetry

The SDK can emit OpenTelemetry spans for each HTTP request. Install
`opentelemetry-instrumentation-requests` to enable automatic tracing or provide your own
tracer to :class:`imednet.core.client.Client`.

## Documentation

The documentation is no longer automatically deployed or published online. To
view the documentation, you must build it locally using Sphinx. The output will
be in `docs/_build/html`.

You can build the docs using the included Makefile target:

```bash
make docs
```

This installs the development dependencies and automatically regenerates the API
documentation before running the Sphinx build. If you prefer, you can run the
commands manually:

```bash
./scripts/setup.sh
poetry run sphinx-apidoc -o docs imednet
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
