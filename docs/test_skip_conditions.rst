Test Skip Conditions
====================

The test suite contains several checks that are skipped unless certain optional
requirements are satisfied. This document summarizes each condition so that local
runs match the behaviour seen in CI.

End-to-End Tests
----------------
The files under ``tests/live`` exercise the SDK against a real iMednet
environment. All of these tests are skipped unless ``IMEDNET_RUN_E2E=1`` and
valid credentials are supplied (see :doc:`configuration`).

Additional variables may be required (see :doc:`configuration` for a full list):

- ``IMEDNET_BATCH_ID`` — used for job polling tests. When unset, the suite
  creates a record to generate a batch ID automatically.
- ``IMEDNET_FORM_KEY`` — optional override for record creation. If not
  supplied, the first form returned by the API is used.
- ``IMEDNET_ALLOW_MUTATION=1`` — enables workflow tests that submit data.

Several integration tests rely on optional packages:

- ``openpyxl`` for Excel exports.
- ``pyarrow`` for Parquet exports.
- ``sqlalchemy`` for SQL exports.
- ``airflow`` for Airflow operators, hooks, and DAG execution tests.

If these packages are missing, the respective tests will be skipped.

Unit Test Exceptions
--------------------
``tests/unit/test_models.py`` skips certain parameter combinations when a model
contains no integer field or uses a pydantic root model. These are normal and do
not indicate missing dependencies.

Running the full suite without any optional variables or packages typically
reports around 90 skipped tests, matching the CI configuration.
