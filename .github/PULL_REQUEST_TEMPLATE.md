## Description
A clear and concise description of what this PR changes and why.

## Related Issue
Closes # <!-- issue number — required -->

## Type of Change

- [ ] Bug fix
- [ ] New feature / capability
- [ ] Refactor (internal restructure, no behavior change)
- [ ] Tech debt / code quality
- [ ] Documentation update
- [ ] CI / tooling change
- [ ] Security fix

## Surface Impact

- [ ] No public API change
- [ ] Public SDK API changed (method signature, return type, model field)
- [ ] CLI interface changed (command name, flag, help text, exit code)
- [ ] Environment variable or configuration key added/changed/removed
- [ ] Breaking change — migration note added to PR description

## How Has This Been Tested?
Describe the tests added or updated. If tests were intentionally skipped, explain why.

## Quality Gate Checklist

### Formatting & linting
- [ ] `poetry run ruff format --check .`
- [ ] `poetry run ruff check .`

### Type checking (run for each affected package)
- [ ] `poetry run mypy packages/core/src/imednet`
- [ ] `poetry run mypy packages/plugins-workflows/src/imednet_workflows` _(if workflows changed)_
- [ ] `poetry run mypy packages/providers-airflow/src/apache_airflow_providers_imednet` _(if Airflow changed)_

### Tests
- [ ] `poetry run pytest -q --cov=imednet --cov=imednet_workflows --cov=apache_airflow_providers_imednet --cov-fail-under=90`
- [ ] All new and existing tests pass
- [ ] Coverage remains >= 90%

### Docs
- [ ] `make docs` runs with zero warnings _(required when public API or CLI surface changed)_
- [ ] Docstrings added or updated for changed public symbols
- [ ] `docs/` pages updated if user-visible behavior changed

### Process
- [ ] PR title follows [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `docs:`, etc.)
- [ ] This PR is linked to an issue above
- [ ] New modules align with package boundaries described in `AGENTS.md`
- [ ] No secrets, tokens, or credentials added to source code
