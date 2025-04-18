# Coding Standards

This document outlines the coding standards and conventions to be followed in the `imednet-python-sdk` project.

## General Principles

* **Readability:** Code should be easy to read and understand. Prioritize clarity over brevity.
* **Consistency:** Follow established patterns and conventions throughout the codebase.
* **Simplicity:** Prefer simple solutions over complex ones (KISS - Keep It Simple, Stupid).
* **Maintainability:** Write code that is easy to modify and debug.

## Python Style Guide (PEP 8)

* Adhere strictly to [PEP 8](https://www.python.org/dev/peps/pep-0008/).
* Use a linter (like `ruff` or `flake8`) and formatter (`black`) to enforce PEP 8 automatically (configured via `pre-commit`).
* Maximum line length: 78 characters (enforced by `black`).

## Naming Conventions

* **Modules:** `lowercase_with_underscores.py`
* **Packages:** `lowercase_with_underscores`
* **Classes:** `CapWords` (e.g., `ImednetClient`)
* **Methods/Functions:** `lowercase_with_underscores()`
* **Variables:** `lowercase_with_underscores`
* **Constants:** `ALL_CAPS_WITH_UNDERSCORES`
* **Private Members:** Prefix with a single underscore (`_private_method`, `_internal_variable`). Avoid using double underscores (`__mangled`) unless necessary for name mangling.

## Docstrings (PEP 257)

* Follow [PEP 257](https://www.python.org/dev/peps/pep-0257/) conventions.
* Use Google-style docstrings (as supported by Sphinx's `napoleon` extension).
* Every public module, class, method, and function should have a docstring.
* Docstrings should explain *what* the code does and *why*, not just *how*.

```python
def example_function(param1, param2):
    """Example function demonstrating docstring format.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        ValueError: If param1 is negative.
    """
    if param1 < 0:
        raise ValueError("param1 cannot be negative")
    # ... function logic ...
    return True
```

## Type Hinting (PEP 484)

* Use type hints extensively for function signatures and variables where appropriate ([PEP 484](https://www.python.org/dev/peps/pep-0484/)).
* Use tools like `mypy` for static type checking (configured via `pre-commit`).
* Use forward references (strings) or `from __future__ import annotations` if needed for complex types or circular dependencies.

```python
from typing import List, Optional

def process_data(data: List[str], threshold: Optional[int] = None) -> bool:
    # ... function logic ...
    pass
```

## Imports

* Import standard library modules first, then third-party libraries, then local application modules.
* Separate import groups with a blank line.
* Use absolute imports where possible.
* Use `isort` (via `ruff` or standalone) to automatically sort imports (configured via `pre-commit`).

## Error Handling

* Define custom exception classes inheriting from standard exceptions where appropriate (e.g., `ImednetError(Exception)`).
* Be specific about the exceptions caught.
* Avoid catching generic `Exception` unless absolutely necessary and re-raising or logging appropriately.

## Testing

* Use `pytest` as the testing framework.
* Write unit tests for individual components (classes, functions).
* Write integration tests where necessary to test interactions between components.
* Aim for high test coverage.
* Use mocking libraries (`pytest-mock`, `respx`) effectively.
* Tests should be placed in the `tests/` directory, mirroring the structure of the `imednet_sdk/` directory.

## Commit Messages

* Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
* Example: `feat: add user authentication endpoint`
* Example: `fix: correct calculation in data processing`
* Example: `docs: update README with setup instructions`
* Example: `refactor: simplify client request logic`
* Example: `test: add tests for edge cases in parser`

## Documentation

* Maintain documentation in the `docs/` directory.
* Use reStructuredText (`.rst`) for Sphinx documentation.
* Use Markdown (`.md`) for other documentation files (like this one).
* Keep documentation up-to-date with code changes.

## Dependencies

* List runtime dependencies in `pyproject.toml` (or `requirements.txt` / `setup.py` if not using `pyproject.toml` fully yet).
* List development dependencies in `requirements-dev.txt` or a `[tool.poetry.group.dev.dependencies]` section in `pyproject.toml`.
* Pin dependency versions to ensure reproducible builds, but allow for compatible updates (e.g., `httpx>=0.25,<0.28`).
