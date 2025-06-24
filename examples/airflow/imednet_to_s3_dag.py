from datetime import datetime

from imednet.integrations.airflow import ImednetToS3Operator

from airflow import DAG

"""Example DAG using :class:`ImednetToS3Operator` to export data to S3.

Configuration notes:
- Create an Airflow connection with ``conn_id`` ``imednet_default`` (or pass a
  custom ``imednet_conn_id``). The connection should provide your iMednet
  ``api_key`` and ``security_key`` either via the login/password fields or the
  ``extra`` JSON. ``base_url`` may also be supplied in ``extra`` when using a
  non‑default iMednet environment. If these values are not set on the
  connection the operator falls back to ``IMEDNET_API_KEY``,
  ``IMEDNET_SECURITY_KEY`` and ``IMEDNET_BASE_URL`` environment variables.
- An AWS connection (``aws_default`` by default) is used by ``S3Hook`` to write
  the JSON output. You can override it via ``aws_conn_id``.

Replace ``STUDY_KEY`` and the S3 parameters with real values before running the
DAG.
"""

default_args = {"start_date": datetime(2024, 1, 1)}

with DAG(
    dag_id="imednet_to_s3_example",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:
    export_records = ImednetToS3Operator(
        task_id="export_records",
        study_key="STUDY_KEY",
        s3_bucket="your-bucket",
        s3_key="imednet/records.json",
        endpoint="records",
        endpoint_kwargs={"page_size": 100},
    )
