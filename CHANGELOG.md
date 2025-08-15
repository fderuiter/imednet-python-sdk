# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Documented contributor setup and process in docs and README.
- Expanded architecture overview with component descriptions and new diagrams.
- Added configuration guide summarizing environment variables and `.env` support.
- Added test for initial SDK retry policy propagation to sync and async clients.
- Added tests for ImednetSDK credential validation.
- Added tests for `records_to_dataframe` and `export_records_csv` covering
  non-flattened and empty inputs.
- Fixed export helpers to cast DataFrame column names to strings before
  case-insensitive de-duplication.
- Imported Airflow hooks at runtime in export operator to simplify mocking.
- Guarded Airflow hook against non-string connection extras and ensured sensors module is importable for reloading.
- Narrowed subject existence validation in `RegisterSubjectsWorkflow` to catch only `ApiError` and `ValueError`.
- Updated smoke workflow to use `actions/upload-artifact@v4`.
- Added tests for JsonModel type normalization.
- Added tests for deprecated `imednet.airflow` shim ensuring warning and re-exports.
- Expanded AGENTS contributor guides with scoped templates across packages and tooling.
- Added negative-path test for `SubjectDataWorkflow.get_all_subject_data` handling empty responses.
- Smoke workflow now uploads verbose script logs and runs live tests with full output.
- Refined contributor guides: mapped project scope, Python 3.10–3.12 support, and
  unified validation for ruff, black, isort, mypy, and pytest across docs,
  tests, examples, and workflows.
- CLI now closes the SDK after each command to free resources and avoid
  interrupt-driven exit codes in repeated invocations.
- Fixed generated batch fixture in live tests to submit valid record data by
    populating required variables, ensuring CLI job polling succeeds.
- Split wide SQLite exports across multiple tables to avoid the 2000-column limit.
- Added helpers for live tests and smoke script to auto-discover study and form
  keys, removing the `IMEDNET_FORM_KEY` override.
- Added helpers to discover active site, subject, and interval identifiers and
  updated the smoke record script to use them.
- Smoke record script now validates site and subject availability before posting
  records.
- Form discovery now skips disabled and non-subject forms to avoid invalid form
  key errors during record creation.
- Decoupled live-data discovery from pytest internals and skip the smoke script
  gracefully when no studies or forms are available.
- Bump project version to `0.1.4`.
- Added tests for unknown form validation errors.
- Added async schema validation tests covering cache refresh and batch validation.
- Exposed export helpers in `imednet.integrations.airflow.export` and consolidated job sensor into a module for easier Airflow imports.
- Added unit tests for CLI output helpers `echo_fetch` and `display_list`.
- ISO datetime parser now pads fractional seconds shorter than six digits to
   microsecond precision.
- Added workflow to sanitize PR bodies and comments of `chatgpt.com/codex` links.
- Extracted common logic from `Client` and `AsyncClient` into new `HTTPClientBase`.
- Added `imednet.config` module with `load_config` helper for reading credentials.
- Documented long-format SQL export and added example script.
- Introduced `RetryPolicy` abstraction for configuring request retries.
- Added tests for retry policy handling of response results and non-RequestError exceptions.
- Documented test suite conventions in `tests/AGENTS.md`.
  `Client`, `AsyncClient` and `ImednetSDK` accept a `retry_policy` parameter.
- Added long-format SQL export via `export_to_long_sql` and the `--long-format` CLI option.
- CLI commands now use shared helpers for study arguments and list output to reduce duplication.
- Deduplicated refresh and validation logic in `SchemaValidator` with helper methods.
- Added verbose logging to smoke record script with new `-v/--verbose` flag.
- Smoke-test workflow now streams INFO-level logs for easier debugging.
- Fixed teardown errors in live tests by using the session event loop for
  `async_sdk` teardown.
- Added subject and site validation to `RegisterSubjectsWorkflow` and support for
  ``subjectKey`` in ``RegisterSubjectRequest``.
- Updated `tests/AGENTS.md` to permit hitting the live iMednet API when running the `tests/live` suite.
- Refactored endpoint initialization in `ImednetSDK` using a registry.
- Added `_build_record_payload` helper to `RecordUpdateWorkflow` to deduplicate
  record dictionary construction.
- Smoke test script accepts a configurable `--timeout` and reports detailed
  job failure messages.
- Live tests now discover the first form key automatically and create a job to
  obtain a batch ID, removing the need for `IMEDNET_FORM_KEY` and
  `IMEDNET_BATCH_ID` secrets.
- Extended smoke test job polling timeout to 90 seconds.
- Renamed ``models._base`` to ``models.json_base`` to avoid import confusion.
- Documented the sentinel return value in ``parse_datetime``.
- Replaced placeholder description in ``workflows/record_update.py``.
- Added docstrings to private helpers in ``core/_requester.py``.
- Documented ``SchemaValidator.refresh`` behavior.
- Added tests covering the default sentinel date in ``parse_datetime``.
- Increased timeout in live ``poll_job`` tests to reduce flakiness.
- Organized Airflow integration code into ``hooks``, ``operators`` and ``sensors`` subpackages.
- Grouped CLI commands into dedicated subpackages for easier navigation.
- Fixed ``ImednetHook`` to import configuration from the correct package.
- Unified sync and async `RecordUpdateWorkflow` tests using parametrized fixtures.
- Extracted `_execute_with_retry` into dedicated sync and async variants for
  clearer retry logic.
- Added an `isort` step to pre-commit and CI checks.
- Fixed import order and formatting across the project.
- CI now fails if test coverage drops below 90%.
- Centralized DataFrame creation in export helpers with new ``_records_df``
  to ensure duplicate columns are removed consistently.
- Added variable and form whitelist options to ``export_to_sql`` and CLI
  ``export sql`` command.
- Consolidated polling loops in ``JobPoller`` with shared ``_run_common`` helper.
- Refactored ``RecordUpdateWorkflow`` with private ``_create_or_update_common``
  to share validation and polling between sync and async methods.
- Added ``register_list_command`` helper to DRY up CLI ``list`` commands.
- Unified sync and async ``poll_job`` tests with parametrized fixtures.
- Consolidated ``JobPoller`` tests by parametrizing over sync and async modes.
- Unified ``SchemaValidator`` tests for both sync and async validators.
- Unified study-structure workflow tests across sync and async implementations.
- Documented Sphinx conventions in new `docs/AGENTS.md`.
- Added smoke workflow for live API tests.
- Documented optional `smoke.yml` workflow which uses `APIKEY` and `SECURITYKEY` to run `tests/live`.
- Restricted smoke workflow to manual dispatch by the repository owner.
- Ensured live schema validation tests verify the schema is populated to avoid
  false negatives when the server returns an empty schema.
- ``validate_record_data`` now raises ``ValidationError`` when provided an unknown form key.
- Record submission now checks form existence after schema refresh and raises
  ``ValueError`` for unknown form keys.
- Added ``DataDictionaryLoader`` for loading data dictionaries from CSV files or ZIP archives.
- Added ``typed_values`` helper for deterministic example values and expanded
  smoke record builder to populate one variable per type and accept optional
  identifiers.
- Live tests now reuse ``typed_values`` to submit well-typed record data across
  date, radio/dropdown, memo, and checkbox fields.
- Endpoint smoke tests now post typed records for subject registration,
  scheduled updates, and new record creation.
- Added unit tests for the smoke record builder to verify typed values and
  optional identifiers.
- Added unit tests for discovery helpers covering study, form, site, subject,
  and interval lookups.
- Added unit tests for `sanitize_base_url` to ensure trailing slash and `/api`
  removal.
- Added tests for JSON logging configuration covering formatter import paths.
- Added unit test for `HTTPClientBase.retry_policy` accessor to ensure executor updates.
- Added test verifying `ImednetSDK.retry_policy` updates sync and async clients.
- Documented error handling and custom retry strategies with a runnable example
  and cross-links from overview guides.
- Added async quick start guide, example script, and README references.

## [0.1.4]

## [Released]

## [0.1.3] - 2025-07-07
- Bump project version to `0.1.3` to fix PyPI upload.
### Changed
- Updated Chanagelog.md with 0.1.3 changes.
  
## [0.1.2] - 2025-07-07

### Changed
- Consolidated job polling logic into a reusable ``JobPoller`` supporting sync
  and async flows.
- Updated integration tests to patch `RequestExecutor` and allow non-strict `respx` mocking.
- Airflow operators now obtain ``ImednetSDK`` instances via ``ImednetHook``
  instead of parsing connections directly.
- Introduced ``ListGetEndpointMixin`` to unify ``list`` and ``get`` logic across endpoints.
- Added ``with_sdk`` decorator for CLI commands to centralize SDK creation and
  error handling.
- Introduced ``JsonModel`` base class for shared parsing logic and refactored
  all models to inherit from it.
- Updated package description to clarify this is an unofficial SDK.

### Fixed
- Fix core package missing `Context` re-export.
- Fix Mermaid diagram syntax errors and add validation test to prevent regressions.

## [0.1.1] - 2025-07-02

### Features and Improvements

- Added PyPI, code style (Black), linter (Ruff), and typing (Mypy) badges to `README.md`.
- Added `pandas` to development dependencies for workflow features.
- Added a comprehensive test suite ensuring over 90% coverage.
- Exposed `BaseClient` from the package root and updated import examples.
- Added unit test for `BaseClient` initialization using environment variables.
- Reintroduced automatic documentation deployment to GitHub Pages.
- Documented caching thread-safety and added a quick start guide.
- Added `examples/quick_start.py` demonstrating minimal SDK usage with
  environment variable validation.
- Renamed the project from `imednet-sdk` to `imednet` and updated repository links to `fderuiter/imednet-python-sdk`.
- Added workflow examples `examples/workflows/extract_audit_trail.py` and
  `examples/workflows/queries_by_site.py`.
- Updated imports in all example scripts to use the package root for `ImednetSDK`.
- Updated documentation examples to import `ImednetSDK` from the package root.

### Fixed

- Resolved circular import errors in `imednet/workflows/register_subjects.py` and `imednet/workflows/study_structure.py` by using `typing.TYPE_CHECKING`.
- Updated `urllib3` to version `2.5.0` to address security vulnerabilities.

### Removed

 - Removed obsolete TEST_PLAN.md file.

## [0.1.0] - 2025-04-28

### Initial Features

- Initial release of the iMednet Python SDK.
- Core client (`ImednetClient`) for handling API requests, authentication, and errors.
- Endpoints for Studies, Sites, Users, Intervals, Forms, Variables, Records, Subjects, Visits, Queries, Jobs, Codings, Record Revisions.
- Pydantic models for all API resources with validation.
- Basic utility functions for date parsing and filter string building.
- Initial workflows for Data Extraction, Record Mapping, Subject Registration, Query Management, and Study Structure retrieval.
- Basic CLI interface using Typer.
- Documentation setup with Sphinx.
- CI setup with GitHub Actions (linting, testing, type checking).
- Code formatting with Black and Ruff.
- Initial unit tests (smoke test).
- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `LICENSE`.
