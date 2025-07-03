# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Consolidated job polling logic into a reusable ``JobPoller`` supporting sync
  and async flows.
- Updated integration tests to patch `RequestExecutor` and allow non-strict `respx` mocking.
- Airflow operators now obtain ``ImednetSDK`` instances via ``ImednetHook``
  instead of parsing connections directly.
- Added ``with_sdk`` decorator for CLI commands to centralize SDK creation and
  error handling.
- Updated package description to clarify this is an unofficial SDK.

### Fixed
- Fix core package missing `Context` re-export.

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
