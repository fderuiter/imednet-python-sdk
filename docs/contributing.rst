Contributing
============

This guide summarizes how to set up your environment, validate changes, and submit
pull requests. Please review our `Code of Conduct <../CODE_OF_CONDUCT.md>`__ and
see `CONTRIBUTING.md <../CONTRIBUTING.md>`__ for complete details.

.. toctree::
   :maxdepth: 1
   :caption: Contributor Guides

   issue_management
   project_standards
   triage_playbook

Setup
-----
.. code-block:: bash

   ./scripts/setup.sh

Issue reporting and triage
--------------------------
The project uses a documented issue operating model so epics, work items, and
maintainer triage follow the same rules across the repository.

- Use ``<type>(<area>): <concise outcome>`` issue titles.
- Capture acceptance criteria, test impact, docs impact, and compatibility notes.
- Apply the label taxonomy and lifecycle in ``issue_management``.
- Follow the intake and rewrite workflow in ``triage_playbook``.

Validation
----------
Run these commands and ensure **≥90%** test coverage before opening a pull request:

.. code-block:: bash

   poetry run black --check .
   poetry run isort --check --profile black .
   poetry run ruff check .
   poetry run mypy packages/core/src/imednet
   poetry run mypy packages/plugins-workflows/src/imednet_workflows
   poetry run mypy packages/providers-airflow/src/apache_airflow_providers_imednet
   poetry run pytest -q \
     --cov=imednet \
     --cov=imednet_workflows \
     --cov=apache_airflow_providers_imednet \
     --cov-fail-under=90
   make docs

HTTP transport mocking
----------------------
Use ``respx`` for any test that exercises ``Client`` or ``AsyncClient`` HTTP behavior.
Do not patch ``Client._client.request``, ``AsyncClient._client.request``, or executor
``send`` callables just to intercept outbound ``httpx`` traffic; mock at the transport
layer instead.

When using ``respx``, prefer strict routers so tests cannot leak live requests and stale
routes fail fast:

.. code-block:: python

   import httpx
   import respx

   @respx.mock(assert_all_called=True, assert_all_mocked=True)
   def test_retry_and_query_params() -> None:
       calls = {"count": 0}

       def handler(request: httpx.Request) -> httpx.Response:
           calls["count"] += 1
           assert request.url.params["page"] == "2"
           if calls["count"] == 1:
               raise httpx.RequestError("boom", request=request)
           return httpx.Response(200, json={"items": []})

       route = respx.route(
           method="GET",
           url__regex=r"https://api\.test/items(?:\?.*)?$",
       )
       route.mock(side_effect=handler)

This keeps production clients free of test-only wrappers while still validating request
construction, retry behavior, dynamic URLs, and query parameters.

Release workflow
----------------
Releases are fully automated and driven by merged PR titles:

1. Ensure the PR title uses a Conventional Commit prefix. Supported prefixes are ``feat:``,
   ``fix:``, ``chore:``, ``docs:``, ``ci:``, ``test:``, ``refactor:``, ``perf:``, and
   ``revert:``. CI enforces this via the ``Semantic PR Title`` check.
2. Run validation locally:

   .. code-block:: bash

      poetry run black --check .
      poetry run isort --check --profile black .
      poetry run ruff check .
      poetry run mypy packages/core/src/imednet
      poetry run mypy packages/plugins-workflows/src/imednet_workflows
      poetry run mypy packages/providers-airflow/src/apache_airflow_providers_imednet
      poetry run pytest -q \
        --cov=imednet \
        --cov=imednet_workflows \
        --cov=apache_airflow_providers_imednet \
        --cov-fail-under=90
      make docs

3. Merge to ``main`` with **Squash and merge** so the PR title becomes the merged commit message.
4. The ``Automated Release`` workflow runs ``release-please`` in manifest mode on ``main`` pushes
   and opens/updates a Release PR with semantic version and changelog updates for the package
   manifests under ``packages/``.
5. Maintainers trigger publication by approving and merging the bot-created Release PR.

Configuration requirements:

- Package versions in ``packages/*/pyproject.toml`` must never be edited manually; ``release-please``
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
