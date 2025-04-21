# Contributing to imednet-python-sdk

First off, thank you for considering contributing to the `imednet-python-sdk`! Your help is appreciated, and every contribution makes a difference.

This document provides guidelines for contributing to this project. Please read it carefully to ensure a smooth and effective contribution process.

## Table of Contents

* [Code of Conduct](#code-of-conduct)
* [How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
* [Development Setup](#development-setup)
* [Style Guides](#style-guides)
  * [Python Code](#python-code)
  * [Commit Messages](#commit-messages)
  * [Documentation](#documentation)
* [Testing](#testing)
* [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Code of Conduct

This project and everyone participating in it are governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers. (Note: We'll need to add a CODE_OF_CONDUCT.md file, perhaps based on the Contributor Covenant standard).

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as [GitHub issues](https://github.com/FrederickdeRuiter/imednet-python-sdk/issues). Before reporting a bug, please check if the issue has already been reported.

When reporting a bug, please include as much detail as possible:

* **Use a clear and descriptive title.**
* **Describe the exact steps to reproduce the bug.**
* **Explain the behavior you observed and why you believe it's a bug.**
* **Explain the behavior you expected to see.**
* **Include details about your environment:**
  * Python version
  * `imednet-python-sdk` version
  * Operating System
* **Include relevant code snippets or examples.**
* **If possible, provide a minimal reproducible example.**

Use the "Bug Report" issue template if available.

### Suggesting Enhancements

Enhancement suggestions are also tracked as [GitHub issues](https://github.com/FrederickdeRuiter/imednet-python-sdk/issues). Before suggesting an enhancement, please check if a similar suggestion already exists.

When suggesting an enhancement:

* **Use a clear and descriptive title.**
* **Provide a step-by-step description of the suggested enhancement.**
* **Explain why this enhancement would be useful.**
* **Provide examples of how the enhancement would be used.**
* **Consider potential drawbacks or alternative solutions.**

Use the "Feature Request" issue template if available.

### Your First Code Contribution

Unsure where to begin contributing? Look for issues tagged `good first issue` or `help wanted`. These are typically issues that are well-defined and suitable for newcomers.

### Pull Requests

Pull Requests (PRs) are the primary way to contribute code changes.

1. **Fork the repository** and create your branch from `main`.
2. **Set up your development environment** (see [Development Setup](#development-setup)).
3. **Make your changes.** Ensure you adhere to the [Style Guides](#style-guides).
4. **Add tests** for your changes. Ensure all tests pass, including existing ones.
5. **Update documentation** if your changes affect public APIs or usage.
6. **Ensure your commit messages are descriptive** and follow the [Conventional Commits](#commit-messages) format.
7. **Push your changes** to your fork.
8. **Open a Pull Request** against the `main` branch of the original repository.
9. **Provide a clear description** of your PR, linking to any relevant issues (e.g., `Fixes #123`).
10. **Be prepared to address feedback** from maintainers and reviewers.

## Development Setup

1. **Clone your fork:** `git clone https://github.com/YOUR_USERNAME/imednet-python-sdk.git`
2. **Navigate to the directory:** `cd imednet-python-sdk`
3. **Create a virtual environment:** `python -m venv .venv`
4. **Activate the virtual environment:**
    * Windows (pwsh): `.\.venv\Scripts\Activate.ps1`
    * Windows (cmd): `.venv\Scripts\activate.bat`
    * macOS/Linux: `source .venv/bin/activate`
5. **Install dependencies:** `pip install -r requirements.txt -r requirements-dev.txt`
6. **(Optional but Recommended) Install pre-commit hooks:** `pre-commit install` (This will run linters/formatters automatically before each commit).

## Style Guides

### Python Code

* Strictly follow **PEP 8**.
* Adhere to the specific conventions outlined in the [**Coding Standards document**](docs/coding_standards.md). This includes naming conventions, docstring format (Google style), type hinting, import ordering, and error handling.
* Use `black` for formatting and `ruff` (or `flake8`/`mypy`) for linting and type checking (enforced via pre-commit hooks if installed).

### Commit Messages

* Follow the [**Conventional Commits**](https://www.conventionalcommits.org/en/v1.0.0/) specification.
  * Examples: `feat: ...`, `fix: ...`, `docs: ...`, `style: ...`, `refactor: ...`, `perf: ...`, `test: ...`, `build: ...`, `ci: ...`, `chore: ...`
  * Include a scope if applicable: `feat(api): add new endpoint`
  * Use the imperative mood (e.g., "add feature" not "added feature").

### Documentation

* Public APIs (modules, classes, functions, methods) **must** have comprehensive docstrings (Google style).
* Update user guides (`docs/usage_guide.md`, Sphinx docs in `docs/source/`) as necessary.
* Use reStructuredText (`.rst`) for Sphinx documentation and Markdown (`.md`) for other files.

## Testing

* Use `pytest` for writing and running tests.
* New features **must** include corresponding tests.
* Bug fixes **should ideally** include a test that reproduces the bug.
* Ensure high test coverage.
* Run tests locally using `pytest` in the root directory after activating your virtual environment.
* Tests are located in the `tests/` directory.

## Issue and Pull Request Labels

Labels help categorize and manage issues and PRs. Maintainers will apply relevant labels. Some common labels include:

* `bug`: A confirmed bug.
* `enhancement`: A feature request or improvement.
* `documentation`: Related to documentation changes.
* `good first issue`: Suitable for newcomers.
* `help wanted`: Seeking community contributions.
* `question`: Needs clarification or discussion.
* `wontfix`: Decided not to implement or fix.
* `duplicate`: Reported previously.

Thank you again for your interest in contributing!
