---
name: Pull Request
about: Describe the changes you are making
title: 'feat: '
labels: ''
assignees: ''
---

**Description**
A clear and concise description of the change.

**Related Issue**
Closes # (issue number)

**Type of Change**

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update

**How Has This Been Tested?**
Describe the tests that you ran to verify your changes. If tests were skipped,
note the reason (see `docs/test_skip_conditions.md`).

**Checklist:**

- [ ] I ran `poetry run ruff check --fix .` and `poetry run black --check .`
- [ ] I ran `poetry run mypy imednet`
- [ ] I ran `poetry run pytest -q --cov=imednet --cov-report=xml` and all tests pass
- [ ] My commits follow [Conventional Commits](https://www.conventionalcommits.org/)
- [ ] New modules align with the architecture in `docs/architecture.rst`
- [ ] My code follows the style guidelines (PEP 8, `black`, `ruff`)
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have added or updated documentation as needed
- [ ] Skipped tests match the cases documented in `docs/test_skip_conditions.md`
