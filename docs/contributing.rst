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
   poetry run mypy src/imednet
   poetry run pytest -q

Release workflow
----------------
Releases are fully automated and driven by merged PR titles:

1. Ensure the PR title uses a Conventional Commit prefix. Supported prefixes are ``feat:``,
   ``fix:``, ``chore:``, ``docs:``, ``ci:``, ``test:``, ``refactor:``, ``perf:``, and
   ``revert:``. CI enforces this via the ``Semantic PR Title`` check.
2. Run validation locally:

   .. code-block:: bash

      poetry run ruff check --fix .
      poetry run black --check .
      poetry run isort --check --profile black .
      poetry run mypy src/imednet
      poetry run pytest -q

3. Merge to ``main`` with **Squash and merge** so the PR title becomes the merged commit message.
4. The ``Automated Release`` workflow runs ``release-please`` on ``main`` pushes and opens/updates
   a Release PR with semantic version and changelog updates.
5. Maintainers trigger publication by approving and merging the bot-created Release PR.

Configuration requirements:

- ``project.version`` in ``pyproject.toml`` must never be edited manually; ``release-please``
  updates it automatically in the generated Release PR changeset.

- Publishing requires ``PYPI_API_TOKEN`` in repository secrets (or migration to PyPI Trusted
  Publishers/OIDC).

- Configure branch protection on ``main`` to require pull request reviews and required checks,
  including ``Semantic PR Title``.

Conventions
-----------
- Apply DRY and SOLID principles.
- Limit lines to 100 characters.
- Use Conventional Commit prefixes in PR titles.

Pull request process
--------------------
- Include paths changed and validation output in the PR description.
- Add or update tests with any code change.
- Update docs and examples for public API or CLI changes.
