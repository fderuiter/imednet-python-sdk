import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
from imednet.integrations import export as export_mod


def test_export_to_csv_and_sql(tmp_path, monkeypatch):
    df = pd.DataFrame({"a": [1]})
    df.to_sql = MagicMock()
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))

    out_csv = tmp_path / "out.csv"
    export_mod.export_to_csv(MagicMock(), "S", str(out_csv))
    assert out_csv.exists()

    sa_module = ModuleType("sqlalchemy")
    engine = MagicMock()
    sa_module.create_engine = MagicMock(return_value=engine)
    monkeypatch.setitem(sys.modules, "sqlalchemy", sa_module)

    export_mod.export_to_sql(MagicMock(), "S", "t", "sqlite://")
    sa_module.create_engine.assert_called_once_with("sqlite://")
    df.to_sql.assert_called_once()


def test_imednet_export_operator(monkeypatch):
    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            return SimpleNamespace(login="K", password="S", extra_dejson={})

    class DummyBaseOperator:
        template_fields = ()

        def __init__(self, **kwargs):
            pass

    hooks_base.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator
    hooks_pkg.base = hooks_base
    airflow.hooks = hooks_pkg
    airflow.models = models_mod
    monkeypatch.setitem(sys.modules, "airflow", airflow)
    monkeypatch.setitem(sys.modules, "airflow.hooks", hooks_pkg)
    monkeypatch.setitem(sys.modules, "airflow.hooks.base", hooks_base)
    monkeypatch.setitem(sys.modules, "airflow.models", models_mod)

    from imednet.integrations.airflow import ImednetExportOperator

    hook = MagicMock(get_conn=MagicMock(return_value=MagicMock()))
    monkeypatch.setattr("imednet.integrations.airflow.ImednetHook", MagicMock(return_value=hook))
    monkeypatch.setattr(export_mod, "export_to_csv", MagicMock())

    op = ImednetExportOperator(task_id="t", study_key="S", output_path="p")
    result = op.execute({})

    export_mod.export_to_csv.assert_called_once_with(hook.get_conn(), "S", "p")
    assert result == "p"
    sys.modules.pop("imednet.integrations.airflow", None)
