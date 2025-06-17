from datetime import datetime

from imednet.integrations.airflow import ImednetExportOperator

from airflow import DAG

"""Example DAG showing :class:`ImednetExportOperator` to write records to a file.

Update ``STUDY_KEY`` and ``output_path`` before running. Credentials are read from
an Airflow connection ``imednet_default`` (or override ``imednet_conn_id``).
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
        output_path="/tmp/records.csv",
        export_func="export_to_csv",
    )
