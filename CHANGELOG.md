# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- CLI now closes the SDK after each command to free resources and avoid
  interrupt-driven exit codes in repeated invocations.
- Fixed generated batch fixture in live tests to submit valid record data by
    populating required variables, ensuring CLI job polling succeeds.
- Split wide SQLite exports across multiple tables to avoid the 2000-column limit.
- Added helpers for live tests and smoke script to auto-discover study and form
  keys, removing the `IMEDNET_FORM_KEY` override.
- Decoupled live-data discovery from pytest internals and skip the smoke script
  gracefully when no studies or forms are available.
- Bump project version to `0.1.4`.
- Added tests for unknown form validation errors.
- ISO datetime parser now pads fractional seconds shorter than six digits to
   microsecond precision.
- Added workflow to sanitize PR bodies and comments of `chatgpt.com/codex` links.
- Extracted common logic from `Client` and `AsyncClient` into new `HTTPClientBase`.
- Added `imednet.config` module with `load_config` helper for reading credentials.
- Introduced `RetryPolicy` abstraction for configuring request retries.
- Documented test suite conventions in `tests/AGENTS.md`.
  `Client`, `AsyncClient` and `ImednetSDK` accept a `retry_policy` parameter.
- Added long-format SQL export via `export_to_long_sql` and the `--long-format` CLI option.
- CLI commands now use shared helpers for study arguments and list output to reduce duplication.
- Deduplicated refresh and validation logic in `SchemaValidator` with helper methods.
- Fixed teardown errors in live tests by using the session event loop for
  `async_sdk` teardown.
- Updated `tests/AGENTS.md` to permit hitting the live iMednet API when running the `tests/live` suite.
- Refactored endpoint initialization in `ImednetSDK` using a registry.
- Added `_build_record_payload` helper to `RecordUpdateWorkflow` to deduplicate
  record dictionary construction.
- Live tests now discover the first form key automatically and create a job to
  obtain a batch ID, removing the need for `IMEDNET_FORM_KEY` and
  `IMEDNET_BATCH_ID` secrets.
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
