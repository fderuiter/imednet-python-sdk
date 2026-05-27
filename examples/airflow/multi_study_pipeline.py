from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from airflow import DAG
from airflow.decorators import task

from apache_airflow_providers_imednet import ImednetExportOperator, ImednetHook

"""Production reference DAG for multi-study exports with dynamic task mapping.

Pattern:
- Upstream TaskFlow discovery is lightweight and returns JSON-serializable work.
- Downstream mapped provider operator performs study-level export execution.

Operational guardrails:
- Discovery and export tasks use retries and execution timeouts.
- The DAG limits parallel workload with ``max_active_runs``/``max_active_tasks``.
- Exports run in an Airflow pool (``imednet_exports``) for shared resource control.
"""

default_args = {
    "start_date": datetime(2024, 1, 1),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="imednet_multi_study_reference",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=8,
    tags=["imednet", "reference", "dynamic-mapping"],
) as dag:

    @task(
        task_id="discover_studies",
        retries=1,
        retry_delay=timedelta(minutes=2),
        execution_timeout=timedelta(minutes=5),
    )
    def discover_export_targets() -> list[dict[str, Any]]:
        """Enumerate per-study export targets only (no extraction or writes)."""
        hook = ImednetHook("imednet_default")
        return [
            {
                "study_key": study_key,
                "output_path": f"/tmp/imednet_exports/{study_key}.csv",
                "export_kwargs": {"index": False},
            }
            for study_key in hook.list_study_keys()
        ]

    ImednetExportOperator.partial(
        task_id="export_records",
        export_func="export_to_csv",
        imednet_conn_id="imednet_default",
        pool="imednet_exports",
        retries=3,
        retry_delay=timedelta(minutes=10),
        execution_timeout=timedelta(minutes=30),
    ).expand_kwargs(discover_export_targets())
