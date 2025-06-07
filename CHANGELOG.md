# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
This file is automatically updated by the release process.

## [Unreleased]

### Features and Improvements

- Added PyPI, code style (Black), linter (Ruff), and typing (Mypy) badges to `README.md`.
- Added `pandas` to development dependencies for workflow features.
- Created `TEST_PLAN.md` outlining steps to achieve 90% test coverage.
- Documented a new "Design Principles" section in `AGENTS.md` encouraging
  modular, DRY, and SOLID code.
- Added helper `validate_record_for_upsert` for Veeva Vault record validation.
- Removed the Flask-based web UI and associated templates to focus on the CLI.
- Added helper `collect_required_fields_and_picklists` for retrieving required
  fields and picklist options from Vault.
- Added method `VeevaVaultClient.collect_required_fields_and_picklists` for
  fetching required fields and picklists directly from the client.
- Added configurable `default_page_size` for SDK pagination.
- Added enrollment dashboard workflow and CLI command to export site enrollment
  summaries.
- Added `VisitCompletionWorkflow` and CLI command `workflows visit-completion` to
  summarize visit progress for a subject.
- Added additional workflows and CLI commands:
  `QueryAgingWorkflow`, `CodingReviewWorkflow`, `SitePerformanceWorkflow`,
  `SubjectEnrollmentDashboard`, `AuditAggregationWorkflow`, `VeevaPushWorkflow`,
  and `VisitTrackingWorkflow`.
- Introduced `InventoryManagementWorkflow` for retrieving device catalog items.
- Updated project to require Python 3.12 only.
- Consolidated pagination logic for all endpoints using new `build_paginator` helper to keep sync and async APIs aligned.
- Fixed codings endpoint unit tests not executing by relocating functions outside
  of another test and ensuring paginator helper is exercised.

### Fixed

- Resolved circular import errors in `imednet/workflows/register_subjects.py` and `imednet/workflows/study_structure.py` by using `typing.TYPE_CHECKING`.

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

[Unreleased]: https://github.com/Bright-Research/imednet-python-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Bright-Research/imednet-python-sdk/releases/tag/v0.1.0
