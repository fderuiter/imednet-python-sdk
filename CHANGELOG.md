# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Bump project version to `0.1.4`.
- Extracted common logic from `Client` and `AsyncClient` into new `HTTPClientBase`.
- Added `imednet.config` module with `load_config` helper for reading credentials.
- Introduced `RetryPolicy` abstraction for configuring request retries.
 - Documented test suite conventions in `tests/AGENTS.md`.
  `Client`, `AsyncClient` and `ImednetSDK` accept a `retry_policy` parameter.
- CLI commands now use shared helpers for study arguments and list output to reduce duplication.
- Deduplicated refresh and validation logic in `SchemaValidator` with helper methods.
- Refactored endpoint initialization in `ImednetSDK` using a registry.
- Added `_build_record_payload` helper to `RecordUpdateWorkflow` to deduplicate
  record dictionary construction.
- Renamed ``models._base`` to ``models.json_base`` to avoid import confusion.
- Documented the sentinel return value in ``parse_datetime``.
- Replaced placeholder description in ``workflows/record_update.py``.
- Added docstrings to private helpers in ``core/_requester.py``.
- Added tests covering the default sentinel date in ``parse_datetime``.
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
- Consolidated polling loops in ``JobPoller`` with shared ``_run_common`` helper.
- Refactored ``RecordUpdateWorkflow`` with private ``_create_or_update_common``
  to share validation and polling between sync and async methods.
- Added ``register_list_command`` helper to DRY up CLI ``list`` commands.
- Unified sync and async ``poll_job`` tests with parametrized fixtures.
- Consolidated ``JobPoller`` tests by parametrizing over sync and async modes.
- Unified ``SchemaValidator`` tests for both sync and async validators.
- Unified study-structure workflow tests across sync and async implementations.
- Documented Sphinx conventions in new `docs/AGENTS.md`.

## [0.1.4] 

## [Released]

## [0.1.3] - 2025-07-07
- Bump project version to `0.1.3` to fix PyPI upload.
### Changed
- Updated Chanagelog.md with 0.1.3 changes.
  
## [0.1.2] - 2025-07-07

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
