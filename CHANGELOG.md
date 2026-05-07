# Changelog

## [0.5.3](https://github.com/fderuiter/imednet-python-sdk/compare/v0.5.2...v0.5.3) (2026-05-07)


### Bug Fixes

* address code review - improve close() error message and add __exit__ test coverage ([deb45c7](https://github.com/fderuiter/imednet-python-sdk/commit/deb45c797e7e486b35cbed13fcb714c490186c7a))
* clarify close() error message, override close() in AsyncImednetSDK to raise TypeError, add test, fix black formatting ([91c5f58](https://github.com/fderuiter/imednet-python-sdk/commit/91c5f58db1c6c318fc7ecec15d83c5e227774a18))
* enforce strict async/sync lifecycle separation in SDK (remove asyncio bridging anti-pattern) ([38c93a7](https://github.com/fderuiter/imednet-python-sdk/commit/38c93a7950d0137a648123b37e46a7b7ebf0d9df))

## [0.5.2](https://github.com/fderuiter/imednet-python-sdk/compare/v0.5.1...v0.5.2) (2026-05-07)


### Bug Fixes

* address PR review thread issues for plugin loading and docs refs ([2c841e0](https://github.com/fderuiter/imednet-python-sdk/commit/2c841e0288a206af737891904ee00c4b7fc666a4))
* tighten workflow init errors and airflow s3 fallback messaging ([b706b3c](https://github.com/fderuiter/imednet-python-sdk/commit/b706b3c04691566b5fd6c632a93eaea30307e419))


### Documentation

* fix sub-package path consistency in AGENTS.md ([00c4847](https://github.com/fderuiter/imednet-python-sdk/commit/00c4847f19fdc39ebf51a498182aeb387d96fb5e))
* rewrite AGENTS.md per issue phases 1-5 ([b242550](https://github.com/fderuiter/imednet-python-sdk/commit/b24255051bffa6aed2aa111928b575eae6ba10bb))

## [0.5.1](https://github.com/fderuiter/imednet-python-sdk/compare/v0.5.0...v0.5.1) (2026-05-07)


### Bug Fixes

* apply review-thread metadata and release workflow corrections ([4ebd11b](https://github.com/fderuiter/imednet-python-sdk/commit/4ebd11b7225e1d0e98f521bec496139330303a96))


### Documentation

* add detailed docstring and doctest examples to parse_bool ([81d868f](https://github.com/fderuiter/imednet-python-sdk/commit/81d868f763f37a1ab0f36e56e7c97542fef5a4d4))
* add explicit release workflow guidance ([6fe54ff](https://github.com/fderuiter/imednet-python-sdk/commit/6fe54ffedea2f6027d8ad1cd71b4a3075af16bc6))
* **ci:** finalize release-please and conventional commit guidance ([c8a8cf9](https://github.com/fderuiter/imednet-python-sdk/commit/c8a8cf92f4ac1c0afa09bb662ea5a940b7039450))
* document IMEDNET_BASE_URL in Quick Start ([ca3c0bd](https://github.com/fderuiter/imednet-python-sdk/commit/ca3c0bdda05a415ac51159086dcbb1aa0034dfcb))

## Changelog

## Unreleased

- Adopted PEP 621 project metadata as the single source of truth in `pyproject.toml`.
- Removed redundant metadata fields from `[tool.poetry]`.
- Added automated semantic versioning and release PR generation via `release-please`.
- Removed the redundant `requests` dependency and standardized SDK HTTP transport on `httpx`.
