from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_dag_runs(monkeypatch):
    pytest.importorskip("airflow")
    from airflow.models import DAG, TaskInstance
    from airflow.utils.state import State
    from imednet.integrations.airflow import ImednetJobSensor, ImednetToS3Operator

    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="bucket")

    sdk = MagicMock()
    sdk.records.list.return_value = [SimpleNamespace(model_dump=lambda: {"id": 1})]
    sdk.jobs.get.return_value = SimpleNamespace(state="COMPLETED")
    monkeypatch.setattr(ImednetToS3Operator, "_get_sdk", lambda self: sdk)
    monkeypatch.setattr(ImednetJobSensor, "_get_sdk", lambda self: sdk)

    with DAG("d", start_date=datetime(2024, 1, 1)) as dag:
        export = ImednetToS3Operator(
            task_id="export",
            study_key="S",
            s3_bucket="bucket",
            s3_key="key",
        )
        wait = ImednetJobSensor(task_id="wait", study_key="S", batch_id="ID")
        export >> wait

    dagrun = dag.create_dagrun(execution_date=datetime(2024, 1, 1), state=State.RUNNING)

    ti_export = TaskInstance(export, dagrun.execution_date)
    ti_export.task = export
    ti_export.run(ignore_ti_state=True)

    ti_wait = TaskInstance(wait, dagrun.execution_date)
    ti_wait.task = wait
    ti_wait.run(ignore_ti_state=True)

    body = s3.get_object(Bucket="bucket", Key="key")["Body"].read().decode()
    assert "id" in body
