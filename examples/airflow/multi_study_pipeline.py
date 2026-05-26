"""Reference DAG for TaskFlow discovery + mapped iMednet exports.

Create the ``imednet_exports`` pool in Airflow before enabling this DAG.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from apache_airflow_providers_imednet import ImednetExportOperator, ImednetHook


@dag(
    dag_id="imednet_multi_study_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=30),
    },
)
def multi_study_pipeline():
    @task(
        task_id="discover_studies",
        retries=1,
        retry_delay=timedelta(minutes=2),
        execution_timeout=timedelta(minutes=10),
    )
    def discover_studies() -> list[dict[str, str]]:
        hook = ImednetHook()
        return hook.build_export_requests(
            output_root="/tmp/imednet/exports",
            file_extension="csv",
            active_only=True,
        )

    ImednetExportOperator.partial(
        task_id="export_study_records",
        export_func="export_to_csv",
        imednet_conn_id="imednet_default",
        pool="imednet_exports",
        retries=2,
        retry_delay=timedelta(minutes=5),
        execution_timeout=timedelta(minutes=30),
        isolate_output_path=True,
    ).expand_kwargs(discover_studies())


multi_study_pipeline()
