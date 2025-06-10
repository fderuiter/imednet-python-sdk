# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features and Improvements

- CLI commands now default to using the `IMEDNET_STUDY_KEY` environment
  variable for the study key. A new `--study-key` option allows overriding it.

- Added PyPI, code style (Black), linter (Ruff), and typing (Mypy) badges to `README.md`.
- Added `pandas` to development dependencies for workflow features.
- Created `TEST_PLAN.md` outlining steps to achieve 90% test coverage.
- Exposed all workflow helpers through new CLI subcommands.
- Added a Tkinter-based desktop UI (`imednet-ui`) for running workflows with
  encrypted credential storage.
- Support multiple named credential profiles with CLI `--profile` option and
  UI selector.

### Fixed

- Resolved circular import errors in `imednet/workflows/register_subjects.py` and `imednet/workflows/study_structure.py` by using `typing.TYPE_CHECKING`.

### Removed

- Removed GitHub Actions workflow for documentation generation and deployment (docs.yml). Documentation must now be built and viewed locally.

## [0.1.0] - 2025-04-28

### Initial Features

- Initial release of the iMedNet Python SDK.
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
