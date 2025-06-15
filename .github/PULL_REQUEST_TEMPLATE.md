---
name: Pull Request
about: Submit changes to the iMedNet SDK
title: 'feat: '
labels: ''
assignees: ''
---

**Summary**
Describe the intent of the change and which modules (CLI, SDK, workflows,
integrations) are affected.

**Related Issue**
Closes # (issue number)

**Type of Change**

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

**Testing**
Detail the commands or steps used to verify the change.

**Checklist**

- [ ] Title and commits follow [Conventional Commits](https://www.conventionalcommits.org)
- [ ] `poetry run ruff check --fix .`
- [ ] `poetry run black --check .`
- [ ] `poetry run mypy imednet`
- [ ] `poetry run pytest -q`
- [ ] Tests added or updated
- [ ] Documentation updated if needed
- [ ] Architecture notes added when touching core modules

**Architecture Notes**
Describe any design decisions and update `docs/architecture.rst` if applicable.
