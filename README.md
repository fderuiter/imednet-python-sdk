# imednet-python-sdk

[![CI](https://img.shields.io/github/actions/workflow/status/fderuiter/imednet-python-sdk/ci.yml?branch=main)](https://github.com/fderuiter/imednet-python-sdk/actions/workflows/ci.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/Ruff-checked-green?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
[![Last commit](https://img.shields.io/github/last-commit/fderuiter/imednet-python-sdk.svg)](https://github.com/fderuiter/imednet-python-sdk/commits/main)

A Python SDK for interacting with the iMednet REST API. Provides client, endpoint wrappers, and data models for all resources.

See the [Changelog](CHANGELOG.md) for release history.

Full project documentation is published at
[https://fderuiter.github.io/imednet-python-sdk/](https://fderuiter.github.io/imednet-python-sdk/).

iMednet API Documentation can be found here:
https://portal.prod.imednetapi.com/

## Features

- Simple, consistent interface for API calls
- Automatic pagination
- Data models for requests and responses
- Workflow utilities for data extraction and mapping
- Pandas helpers for DataFrame conversion and CSV export
- Optional in-memory caching for study, form, interval, and variable listings
  (not thread-safe; refresh or recreate the SDK in long running processes)
- Structured JSON logging with optional OpenTelemetry tracing
- Async client and CLI for common tasks

Calls to `sdk.studies.list()`, `sdk.forms.list()`, `sdk.intervals.list()` and
`sdk.variables.list()` cache results in memory. Pass `refresh=True` to bypass
the cache. See `docs/caching.rst` for details.

## Installation

```bash
pip install imednet
```

Or install from source:

```bash
git clone https://github.com/fderuiter/imednet-python-sdk.git
cd imednet-python-sdk
./scripts/setup.sh
```

## Quick Start

Enable structured logging, create an SDK instance and list studies:

```python
from imednet import ImednetSDK
from imednet.utils import configure_json_logging

configure_json_logging()
sdk = ImednetSDK()
print(sdk.studies.list())
```
Run `python examples/quick_start.py` for a runnable version that checks your
environment variables.

## Usage

First, ensure you have set your iMednet API credentials as environment variables.
Keep these keys secure and never commit them to source control:

```powershell
# For PowerShell:
$env:IMEDNET_API_KEY="your_api_key_here"
$env:IMEDNET_SECURITY_KEY="your_security_key_here"
# Optional: Set if using a non-standard base URL

# $env:IMEDNET_BASE_URL="https://your.imednet.instance"

# For Bash/Zsh:
# export IMEDNET_API_KEY="your_api_key_here"
# export IMEDNET_SECURITY_KEY="your_security_key_here"
# export IMEDNET_BASE_URL="https://your.imednet.instance"
```

### Using the Python SDK

Then, you can use the SDK like this:

```python
import os
import json
from imednet import ImednetSDK
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
from imednet import AsyncImednetSDK

async def main():
    study_key = os.getenv("IMEDNET_STUDY_KEY", "your_study_key_here")
    async with AsyncImednetSDK() as sdk:
        studies = await sdk.studies.async_list()
        print(studies)

# asyncio.run(main())
```


### Record Validation

The SDK can validate record payloads locally using cached form metadata. Create
a :class:`~imednet.validation.cache.SchemaCache` and pass it to
``RecordsEndpoint.create`` or the ``RecordUpdateWorkflow`` methods. A
``ValidationError`` is raised if variables are unknown or required fields are
missing.

```python
from imednet.validation.cache import SchemaCache

schema = SchemaCache()
schema.refresh(sdk.forms, sdk.variables, study_key)
sdk.records.create(study_key, record_data, schema=schema)
```

When using ``AsyncImednetSDK`` the same logic applies asynchronously. Record
payloads can be validated before submission with
``SchemaValidator.validate_batch``:

```python
from imednet import AsyncImednetSDK
from imednet.validation.cache import SchemaValidator

async def submit_records_async(records):
    async with AsyncImednetSDK() as sdk:
        validator = SchemaValidator(sdk)
        await validator.validate_batch(study_key, records)
        await sdk.records.async_create(study_key, records, schema=validator.schema)
```

### Exporting records to CSV

Install the optional pandas dependency and call
``export_records_csv`` to save all records for a study:

```bash
pip install imednet[pandas]
```

```python
from imednet.utils.pandas import export_records_csv

sdk = ImednetSDK()
export_records_csv(sdk, study_key, "records.csv")
```

### Exporting records to Excel

Install `openpyxl` or the pandas `excel` extras to enable Excel export:

```bash
pip install pandas[excel]
```

```python
from imednet.integrations import export

export.export_to_excel(sdk, study_key, "records.xlsx")

### Using the Command Line Interface (CLI)

After installing the package (`pip install imednet`) and setting the environment variables as shown above, you can use the `imednet` command.
Parquet and SQL exports require the optional `pyarrow` and `SQLAlchemy` dependencies:

```bash
pip install "imednet[pyarrow,sqlalchemy]"
```

SQLite imposes a limit of roughly 2000 columns per table. To avoid this
restriction the `imednet export sql` command automatically writes one table
per form when the connection string uses SQLite. Use `--single-table` to
retain the original behaviour. The `export_to_sql_by_form` helper provides
the same functionality for direct Python usage.

Then run commands such as:

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

When using SQLite the helper constant ``imednet.integrations.export.MAX_SQLITE_COLUMNS``
still applies. If a form exceeds this limit an error is raised. Consider another
database backend for very wide forms or specify ``--single-table`` to manually
manage the limitation.

- See the full API reference in the [HTML docs](docs/_build/html/index.html).
- More examples can be found in the `examples/` directory.
- An architecture diagram is available in `docs/architecture.rst`.

### Airflow Integration

Custom operators and sensors integrate with Apache Airflow. Install the package with the ``airflow`` extra:

```bash
pip install 'imednet[airflow]'
```

Example DAG:

```python
from datetime import datetime
from airflow import DAG
from imednet.integrations.airflow import ImednetToS3Operator, ImednetJobSensor

default_args = {"start_date": datetime(2024, 1, 1)}

with DAG(
    dag_id="imednet_example",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:
    export_records = ImednetToS3Operator(
        task_id="export_records",
        study_key="STUDY_KEY",
        s3_bucket="your-bucket",
        s3_key="imednet/records.json",
    )

    wait_for_job = ImednetJobSensor(
        task_id="wait_for_job",
        study_key="STUDY_KEY",
        batch_id="BATCH_ID",
        poke_interval=60,
    )

    export_records >> wait_for_job
```

Create an Airflow connection ``imednet_default`` or override ``imednet_conn_id``.
Provide your API credentials in that connection.
Use the login/password or ``extra`` JSON to provide ``api_key`` and ``security_key``.
``base_url`` may be added in ``extra`` for a non-standard environment.
The operators fall back to ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` if not set.
``ImednetToS3Operator`` also uses an AWS connection (``aws_default`` by default) to write to S3.

When the ``airflow`` package is available the integration tests run
``tests/integration/test_airflow_dag.py`` to execute a small DAG with these
operators. Refer to ``docs/test_skip_conditions.md`` for skip conditions.


### JSON Logging

All logs from the SDK use JSON format so they can be easily parsed. Pass `log_level`
 to `imednet.core.client.Client` to adjust verbosity. Call
 `imednet.utils.configure_json_logging()` if you want to enable the same formatting
 for your entire application.


### Tracing with OpenTelemetry

Install `opentelemetry-instrumentation-requests` to automatically trace HTTP requests or pass your own tracer to `imednet.core.client.Client`.

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

Build and test locally using the same commands as CI:

```bash
./scripts/setup.sh  # run once
poetry run ruff check --fix .
poetry run black --check .
poetry run mypy imednet
poetry run pytest -q --cov=imednet --cov-report=xml
```
The unit test suite covers over 90% of the codebase. When optional packages or
environment variables are missing you should see a number of skipped tests. See
`docs/test_skip_conditions.md` for details.

### End-to-End Tests

A minimal live test suite resides in `tests/live`. These checks exercise several
live endpoints including studies, sites, forms, subjects and records. The tests
are skipped by default and require valid credentials. Set `IMEDNET_RUN_E2E=1`
and provide `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY` (optionally
`IMEDNET_BASE_URL`) to enable them:

```bash
IMEDNET_RUN_E2E=1 IMEDNET_API_KEY=... IMEDNET_SECURITY_KEY=... pytest tests/live
```

Run `./scripts/setup.sh` once before running tests to install the development
dependencies and set up the pre-commit hooks.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Versioning and Releases

This project follows Semantic Versioning (`MAJOR.MINOR.PATCH`).
See [CHANGELOG.md](CHANGELOG.md) for the full release history.

To publish a new release:

1. Update the changelog with the upcoming version notes.
2. Run `poetry version` to bump the version number.
3. Rebuild the documentation so the new version appears in the docs:
   `make docs`
4. Commit the changes and create a tag like `vX.Y.Z`.
5. Push the tag to trigger the workflow in `.github/workflows/release.yml`.

## Governance and Roadmap

This project is currently maintained by Frederick de Ruiter.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
