Airflow Integration
===================

Airflow support is provided via a standalone provider package.

Installation
------------

Install the provider package:

.. code-block:: bash

   pip install "apache-airflow>=3.2.0,<4.0.0" apache-airflow-providers-imednet

For ``ImednetToS3Operator`` support, install the provider's ``amazon`` extra:

.. code-block:: bash

   pip install "apache-airflow>=3.2.0,<4.0.0" "apache-airflow-providers-imednet[amazon]"

Production Reference DAG
------------------------

Use ``examples/airflow/multi_study_pipeline.py`` as the recommended production
pattern for dynamic task mapping deployments. It demonstrates lightweight
TaskFlow discovery feeding mapped provider operators while keeping execution
logic inside mapped tasks.

.. literalinclude:: ../examples/airflow/multi_study_pipeline.py
   :language: python

Operational safeguards highlighted in the reference DAG:

- Discovery only enumerates work items and returns JSON-serializable values.
- Retries and ``execution_timeout`` are configured for both discovery and
  mapped export execution.
- ``max_active_runs`` and ``max_active_tasks`` constrain DAG-level concurrency.
- ``pool`` is set on the mapped operator for shared-resource throttling.

Additional single-purpose DAGs are available in ``examples/airflow/`` for
focused operator/sensor usage patterns.

Connections
-----------

Create an Airflow connection ``imednet_default`` or override ``imednet_conn_id``.
Provide ``api_key`` and ``security_key`` via the login/password fields or in the
``extra`` JSON. ``base_url`` may be added in ``extra`` for a non-standard
environment. The hook merges these settings with values from
``imednet.config.load_config`` so environment variables still apply. The
``ImednetToS3Operator`` also uses an AWS connection (``aws_default`` by default)
when writing to S3.

For task-mapping discovery steps, ``ImednetHook`` provides explicit helper methods:

- ``get_sdk_client()`` returns the live :class:`~imednet.ImednetSDK` for use only
  inside task execution context.
- ``list_studies_metadata()`` returns JSON-serializable primitive dictionaries
  (with sensitive keys redacted) for safe mapped task expansion.
- ``list_study_keys()`` returns primitive study keys only.
- ``describe_connection()`` returns redacted connection metadata and never exposes
  raw credentials.

``get_conn()`` is kept as a backward-compatible alias to ``get_sdk_client()``.

Operators and Sensors
---------------------
The Airflow integration organizes hooks, operators, and sensors in dedicated
subpackages for clarity.

``ImednetExportOperator`` saves records to a local file using helpers from
``imednet.integrations.export``. ``ImednetToS3Operator`` sends JSON data to S3
and ``ImednetJobSensor`` waits for an export job to complete. All operators use
``ImednetHook`` to obtain an :class:`~imednet.ImednetSDK` instance from an
Airflow connection. The production reference DAG above shows the recommended
dynamic-mapping pattern: keep static settings (for example ``export_func`` and
``imednet_conn_id``) in ``.partial(...)`` and map only runtime fields
(``study_key``, ``output_path``, ``export_kwargs``).

.. code-block:: python

   from typing import Any
   from airflow.decorators import task
   from apache_airflow_providers_imednet import ImednetExportOperator, ImednetHook

   @task
   def export_targets() -> list[dict[str, Any]]:
       hook = ImednetHook("imednet_default")
       return [
           {
               "study_key": study_key,
               "output_path": f"/tmp/{study_key}.csv",
               "export_kwargs": {"index": False},
           }
           for study_key in hook.list_study_keys()
       ]

   ImednetExportOperator.partial(
       task_id="export_records",
       export_func="export_to_csv",
       imednet_conn_id="imednet_default",
   ).expand_kwargs(export_targets())

Testing with Airflow
--------------------

The unit tests stub out the Airflow dependencies. When the ``airflow`` package
is installed, ``tests/integration/test_airflow_dag.py`` runs a small DAG with
``ImednetToS3Operator`` and ``ImednetJobSensor``. The test creates a temporary
S3 bucket with ``moto`` and executes the tasks via ``TaskInstance.run``. It is
skipped automatically if Airflow is missing.
