# Development Notes

- Use `pre-commit` to run formatting and linting. Install hooks via `pre-commit install`.
- Code must pass `ruff`, `black`, `mypy`, and `pytest` before committing.
- Run the following checks manually when modifying code or tests:

```bash
poetry run ruff check --fix .
poetry run black --check .
poetry run mypy imednet
poetry run pytest -q
```

- The project enforces a maximum line length of 100 characters.
