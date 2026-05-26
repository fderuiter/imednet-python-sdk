Airflow Integration
===================

Airflow support is provided via a standalone provider package.

Installation
------------

Install the provider package:

.. code-block:: bash

   pip install "apache-airflow>=2.3.0,<4.0.0" apache-airflow-providers-imednet
   # Optional only for ImednetToS3Operator
   pip install "apache-airflow-providers-imednet[amazon]"

Dynamic task mapping pattern
----------------------------

.. code-block:: python

   from datetime import datetime, timedelta
   from airflow.decorators import dag, task
   from apache_airflow_providers_imednet import ImednetExportOperator, ImednetHook

   @dag(
       dag_id="imednet_multi_study_pipeline",
       start_date=datetime(2024, 1, 1),
       schedule=None,
       catchup=False,
       max_active_runs=1,
       default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
   )
   def multi_study_pipeline():
       @task(task_id="discover_studies")
       def discover_studies() -> list[dict[str, str]]:
           hook = ImednetHook()
           return hook.build_export_requests(output_root="/tmp/imednet/exports")

       ImednetExportOperator.partial(
           task_id="export_study_records",
           export_func="export_to_csv",
           isolate_output_path=True,
           pool="imednet_exports",
           execution_timeout=timedelta(minutes=30),
       ).expand_kwargs(discover_studies())

   multi_study_pipeline()

See ``examples/airflow/multi_study_pipeline.py`` for a full production-ready
reference DAG.

Connections
-----------

Create an Airflow connection ``imednet_default`` or override ``imednet_conn_id``.
Provide ``api_key`` and ``security_key`` via the login/password fields or in the
``extra`` JSON. ``base_url`` may be added in ``extra`` for a non-standard
environment. The hook merges these settings with values from
``imednet.config.load_config`` so environment variables still apply. The
``ImednetHook`` also exposes discovery helpers that return only primitive,
serialization-safe values for mapped task expansion:

* ``discover_studies()`` for lightweight study discovery payloads.
* ``build_export_requests()`` for ``.expand_kwargs(...)`` payloads.
* ``resolved_connection_config(redact_credentials=True)`` to inspect effective
  settings with credentials masked.

``ImednetToS3Operator`` uses an AWS connection (``aws_default`` by default) and
requires the optional ``amazon`` extra.

Operators and Sensors
---------------------
The Airflow integration organizes hooks, operators, and sensors in dedicated subpackages for clarity.

``ImednetExportOperator`` saves records to a local file using helpers from
``imednet.integrations.export``. ``ImednetToS3Operator`` sends JSON data to S3
and ``ImednetJobSensor`` waits for an export job to complete. All operators use
``ImednetHook`` to obtain an :class:`~imednet.ImednetSDK` instance from an
Airflow connection at execution time. ``ImednetExportOperator`` can isolate
output paths per mapped task instance by setting ``isolate_output_path=True``.

Testing with Airflow
--------------------

The unit tests stub out the Airflow dependencies. When the ``airflow`` package
is installed, ``tests/integration/test_airflow_dag.py`` runs a small DAG with
``ImednetToS3Operator`` and ``ImednetJobSensor``. The test creates a temporary
S3 bucket with ``moto`` and executes the tasks via ``TaskInstance.run``. It is
skipped automatically if Airflow is missing.
