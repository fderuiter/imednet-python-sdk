from datetime import datetime

from imednet.integrations.airflow import ImednetJobSensor

from airflow import DAG

"""Example DAG demonstrating :class:`ImednetJobSensor` to monitor an iMednet job.

This sensor periodically polls iMednet until the specified job reaches a
terminal state. Configuration is similar to ``ImednetToS3Operator``:
- Credentials are read from the Airflow connection ``imednet_default`` (or a
  custom ``imednet_conn_id``) using the login/password or ``extra`` fields.
  Environment variables ``IMEDNET_API_KEY`` and ``IMEDNET_SECURITY_KEY`` may be
  used as fallbacks.
- ``base_url`` can be provided in ``extra`` or via ``IMEDNET_BASE_URL`` when
  targeting a non‑default environment.

Update ``STUDY_KEY`` and ``BATCH_ID`` with real values before running.
"""

default_args = {"start_date": datetime(2024, 1, 1)}

with DAG(
    dag_id="imednet_job_sensor_example",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
) as dag:
    wait_for_job = ImednetJobSensor(
        task_id="wait_for_job",
        study_key="STUDY_KEY",
        batch_id="BATCH_ID",
        poke_interval=60,
    )
