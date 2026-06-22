"""TODO: Add docstring."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import boto3
import pytest
from moto import mock_aws


@mock_aws
def test_dag_runs(monkeypatch):
    """TODO: Add docstring."""
    pytest.importorskip("airflow")
    from airflow.models import DAG, TaskInstance  # noqa: E402, I001
    from airflow.utils.state import State  # noqa: E402, I001

    from apache_airflow_providers_imednet import ImednetJobSensor, ImednetExportOperator  # noqa: E402, I001

    sdk = MagicMock()
    sdk.records.list.return_value = [SimpleNamespace(model_dump=lambda: {"id": 1})]
    sdk.jobs.get.return_value = SimpleNamespace(state="COMPLETED")
    monkeypatch.setattr(ImednetExportOperator, "_get_sdk", lambda self: sdk)
    monkeypatch.setattr(ImednetJobSensor, "_get_sdk", lambda self: sdk)

    with DAG("d", start_date=datetime(2024, 1, 1)) as dag:
        export = ImednetExportOperator(
            task_id="export",
            study_key="S",
            output_path="/tmp/out.csv",
        )
        wait = ImednetJobSensor(task_id="wait", study_key="S", batch_id="ID")
        export >> wait

    # Note: export_to_csv needs to be mocked so it doesn't fail trying to write the mock data.
    from imednet.integrations import export as export_mod
    monkeypatch.setattr(export_mod, "export_to_csv", MagicMock())

    export.execute(context={})
    wait.execute(context={})

    export_mod.export_to_csv.assert_called_once()
