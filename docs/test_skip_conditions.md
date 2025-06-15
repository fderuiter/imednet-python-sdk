# Test Skip Conditions

The test suite contains several checks that are skipped unless certain optional
requirements are satisfied. This document summarizes each condition so that local
runs match the behaviour seen in CI.

## End-to-End Tests
The files under `tests/live` exercise the SDK against a real iMedNet
environment. All of these tests are skipped unless `IMEDNET_RUN_E2E=1` and valid
credentials are supplied via `IMEDNET_API_KEY` and `IMEDNET_SECURITY_KEY`
(optionally `IMEDNET_BASE_URL`).

Additional variables may be required:

- `IMEDNET_BATCH_ID` &mdash; required for job polling tests.
- `IMEDNET_FORM_KEY` &mdash; required for record creation tests.
- `IMEDNET_ALLOW_MUTATION=1` &mdash; enables workflow tests that submit data.

Several integration tests rely on optional packages:

- `openpyxl` for Excel exports.
- `pyarrow` for Parquet exports.
- `sqlalchemy` for SQL exports.
- `airflow` for Airflow operators and hooks.

If these packages are missing, the respective tests will be skipped.

## Unit Test Exceptions
`tests/unit/test_models.py` skips certain parameter combinations when a model
contains no integer field or uses a pydantic root model. These are normal and do
not indicate missing dependencies.

Running the full suite without any optional variables or packages typically
reports around 89 skipped tests, matching the CI configuration.
