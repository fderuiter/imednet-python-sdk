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
Use this workflow for new releases:

1. Run validation locally:

   .. code-block:: bash

      poetry run ruff check --fix .
      poetry run black --check .
      poetry run isort --check --profile black .
      poetry run mypy src/imednet
      poetry run pytest -q

2. Bump the version:

   .. code-block:: bash

      poetry run bump-my-version patch

   Use ``minor`` or ``major`` when appropriate.

3. Build docs and package artifacts:

   .. code-block:: bash

      make docs
      poetry build

4. Push the release commit and tags:

   .. code-block:: bash

      git push origin <branch-name>
      git push origin --tags

5. Confirm GitHub Actions is green. Publishing is triggered by ``vX.Y.Z`` tags.

Conventions
-----------
- Apply DRY and SOLID principles.
- Limit lines to 100 characters.
- Use Conventional Commit messages.

Pull request process
--------------------
- Include paths changed and validation output in the PR description.
- Add or update tests with any code change.
- Update docs and examples for public API or CLI changes.
