# Strict Typing Tasks

The following tasks outline how to resolve the remaining mypy strict errors.

- [ ] Annotate Pydantic models under `imednet/models`.
- [ ] Add return and argument types to endpoint constructors in `imednet/endpoints`.
- [ ] Remove stale `# type: ignore` comments and provide proper annotations in
  `imednet/workflows`.
- [ ] Fully type command line interface in `imednet/cli.py`.
- [ ] Export expected names from endpoint modules so `mypy` can verify them.
- [ ] Enable strict checks gradually for additional packages in `pyproject.toml`.
