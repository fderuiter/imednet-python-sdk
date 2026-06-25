"""Tests for test_airflow_dag."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


def test_dag_runs(monkeypatch, tmp_path):
    """Test test_dag_runs behavior."""
    pytest.importorskip("airflow")
    out_csv = tmp_path / "out.csv"
    from airflow.models import DAG, TaskInstance  # noqa: E402, I001
    from airflow.utils.state import State  # noqa: E402, I001

    from apache_airflow_providers_imednet import ImednetJobSensor, ImednetExportOperator  # noqa: E402, I001

    sdk = MagicMock()

    import pandas as pd

    df = pd.DataFrame({"id": [1, 2]})
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    from imednet.integrations import export as export_mod

    monkeypatch.setattr(
        export_mod, "_record_mapper", MagicMock(return_value=MagicMock(return_value=mapper_inst))
    )

    sdk.jobs.get.return_value = SimpleNamespace(state="COMPLETED")
    monkeypatch.setattr(ImednetExportOperator, "_get_sdk", lambda self: sdk)
    monkeypatch.setattr(ImednetJobSensor, "_get_sdk", lambda self: sdk)

    with DAG("d", start_date=datetime(2024, 1, 1)) as dag:
        export = ImednetExportOperator(
            task_id="export",
            study_key="S",
            destination="csv",
            output_path=str(out_csv),
        )
        wait = ImednetJobSensor(task_id="wait", study_key="S", batch_id="ID")
        export >> wait

    export.execute(context={})
    wait.execute(context={})
    with open(str(out_csv), 'r') as f:
        body = f.read()
    assert "id" in body
    assert "id" in body
