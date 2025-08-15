Contributing
============

This guide summarizes how to set up your environment, validate changes, and submit
pull requests. Please review our `Code of Conduct <../CODE_OF_CONDUCT.md>`__ and
see `CONTRIBUTING.md <../CONTRIBUTING.md>`__ for complete details.

Setup
-----
.. code-block:: bash

   ./scripts/setup.sh

Validation
----------
Run these commands and ensure **≥90%** test coverage before opening a pull request:

.. code-block:: bash

   poetry run ruff check --fix .
   poetry run black --check .
   poetry run isort --check --profile black .
   poetry run mypy imednet
   poetry run pytest -q

Conventions
-----------
- Apply DRY and SOLID principles.
- Limit lines to 100 characters.
- Use Conventional Commit messages.
- Update ``[Unreleased]`` in ``CHANGELOG.md``.

Pull request process
--------------------
- Include paths changed and validation output in the PR description.
- Add or update tests with any code change.
- Update docs and examples for public API or CLI changes.

