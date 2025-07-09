Airflow Integration
===================

The SDK ships with operators and sensors for building Airflow pipelines.

Installation
------------

Install the SDK together with Airflow and the Amazon provider:

.. code-block:: bash

   pip install imednet apache-airflow apache-airflow-providers-amazon

Example DAG
-----------

.. code-block:: python

   from datetime import datetime
   from airflow import DAG
   from imednet.integrations.airflow import ImednetToS3Operator, ImednetJobSensor

   default_args = {"start_date": datetime(2024, 1, 1)}

   with DAG(
       dag_id="imednet_example",
       schedule_interval=None,
       default_args=default_args,
       catchup=False,
   ) as dag:
       export_records = ImednetToS3Operator(
           task_id="export_records",
           study_key="STUDY_KEY",
           s3_bucket="your-bucket",
           s3_key="imednet/records.json",
       )

       wait_for_job = ImednetJobSensor(
           task_id="wait_for_job",
           study_key="STUDY_KEY",
           batch_id="BATCH_ID",
           poke_interval=60,
       )

       export_records >> wait_for_job

Connections
-----------

Create an Airflow connection ``imednet_default`` or override ``imednet_conn_id``.
Provide ``api_key`` and ``security_key`` via the login/password fields or in the
``extra`` JSON. ``base_url`` may be added in ``extra`` for a non-standard
environment. The hook merges these settings with values from
``imednet.config.load_config`` so environment variables still apply. The
``ImednetToS3Operator`` also uses an AWS connection (``aws_default`` by default)
when writing to S3.

Operators and Sensors
---------------------
The Airflow integration organizes hooks, operators, and sensors in dedicated subpackages for clarity.

``ImednetExportOperator`` saves records to a local file using helpers from
``imednet.integrations.export``. ``ImednetToS3Operator`` sends JSON data to S3
and ``ImednetJobSensor`` waits for an export job to complete. All operators use
``ImednetHook`` to obtain an :class:`~imednet.ImednetSDK` instance from an
Airflow connection.

Testing with Airflow
--------------------

The unit tests stub out the Airflow dependencies. When the ``airflow`` package
is installed, ``tests/integration/test_airflow_dag.py`` runs a small DAG with
``ImednetToS3Operator`` and ``ImednetJobSensor``. The test creates a temporary
S3 bucket with ``moto`` and executes the tasks via ``TaskInstance.run``. It is
skipped automatically if Airflow is missing.
