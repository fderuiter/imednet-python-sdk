=================
Verification Loop
=================

Before proposing any solution, execute and pass all CI quality gates locally.

1. Read ``.github/workflows/main.yml`` (the ``quality`` job) to identify the authoritative lint, format, and type-check commands.
2. Run the full gate in order:

   .. code-block:: bash

      hatch run ruff format --check .
      hatch run ruff check .
      hatch run mypy packages/core/src/imednet
      hatch run mypy packages/plugins-workflows/src/imednet_workflows
      hatch run mypy packages/providers-airflow/src/apache_airflow_providers_imednet
      hatch run pytest -q \
        --cov=imednet \
        --cov=imednet_workflows \
        --cov=apache_airflow_providers_imednet \
        --cov-fail-under=90

3. Fix every reported error before marking a task complete. Re-run until the entire sequence exits 0.
4. Build documentation and confirm zero warnings:

   .. code-block:: bash

      hatch run docs
