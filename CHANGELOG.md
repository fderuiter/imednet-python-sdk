# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial project structure.
- GitHub Actions workflow (`release.yml`) for automated PyPI publishing on tag pushes.
- Codecov integration to CI workflow (`ci.yml`).
- `CHANGELOG.md` file.
- `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.
- `todo.md` for tracking future enhancements.
- Example scripts for retrieving studies, sites, subjects, users, variables, and visits using the iMednet SDK.
- Validators for model fields to normalize and default values; refactored models to utilize new validation logic.

### Changed

- Switched project license from Proprietary to MIT License.
- Updated `README.md` with badges, improved usage examples, installation instructions, and new sections.
- Updated `pyproject.toml` to reflect MIT license and configure included files.
- Refactored models to use new validation logic for field normalization and defaults.

### Removed

- Version management from `imednet/__init__.py` (handled by Poetry).

### Fixed

- Updated default datetime value in `parse_datetime` function.

## [0.1.0] - YYYY-MM-DD
