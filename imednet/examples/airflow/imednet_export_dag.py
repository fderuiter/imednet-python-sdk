from datetime import datetime

from imednet.integrations.airflow import ImednetExportOperator

from airflow import DAG

"""Example DAG using :class:`ImednetExportOperator` to write records to a CSV file.

Configuration notes:
- Create an Airflow connection ``imednet_default`` (or pass a custom
  ``imednet_conn_id``) containing your ``api_key`` and ``security_key``.
  ``base_url`` can be supplied in the connection ``extra`` JSON for non-default
  environments. Environment variables ``IMEDNET_API_KEY`` and
  ``IMEDNET_SECURITY_KEY`` are used as fallbacks.

Replace ``STUDY_KEY`` and ``/tmp/records.csv`` with real values before running.
"""

default_args = {"start_date": datetime(2024, 1, 1)}

with DAG(
    dag_id="imednet_export_example",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:
    export_records = ImednetExportOperator(
        task_id="export_records",
        study_key="STUDY_KEY",
        file_path="/tmp/records.csv",
        flatten=True,
    )
