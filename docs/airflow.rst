Airflow Integration
===================

The SDK ships with operators and sensors for building Airflow pipelines.

Installation
------------

Install the SDK together with Airflow and the Amazon provider:

.. code-block:: bash

   pip install imednet-python-sdk apache-airflow apache-airflow-providers-amazon

Example DAG
-----------

.. code-block:: python

   from datetime import datetime
   from airflow import DAG
   from imednet.airflow import ImednetToS3Operator, ImednetJobSensor

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
environment. The operators fall back to ``IMEDNET_API_KEY`` and
``IMEDNET_SECURITY_KEY`` if the connection lacks these values. The
``ImednetToS3Operator`` also uses an AWS connection (``aws_default`` by default)
when writing to S3.
