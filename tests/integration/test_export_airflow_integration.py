def _setup_airflow(monkeypatch):
    import sys
    from types import ModuleType, SimpleNamespace
    airflow_mod = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_mod = ModuleType("airflow.sdk.bases.hook")
    sdk_mod = ModuleType("airflow.sdk")
    sdk_bases = ModuleType("airflow.sdk.bases")
    sdk_defs = ModuleType("airflow.sdk.definitions")
    sdk_ctx = ModuleType("airflow.sdk.definitions.context")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            return SimpleNamespace(login="K", password="S", extra_dejson={})

    class DummyBaseOperator:
        template_fields = ()
        def __init__(self, **kwargs):
            pass

    hooks_mod.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator

    sdk_bases.hook = hooks_mod
    sdk_mod.bases = sdk_bases
    sdk_defs.context = sdk_ctx
    sdk_mod.definitions = sdk_defs
    airflow_mod.sdk = sdk_mod
    airflow_mod.hooks = hooks_pkg
    airflow_mod.models = models_mod

    monkeypatch.setitem(sys.modules, "airflow", airflow_mod)
    monkeypatch.setitem(sys.modules, "airflow.hooks", hooks_pkg)
    monkeypatch.setitem(sys.modules, "airflow.sdk.bases.hook", hooks_mod)
    monkeypatch.setitem(sys.modules, "airflow.sdk", sdk_mod)
    monkeypatch.setitem(sys.modules, "airflow.sdk.bases", sdk_bases)
    monkeypatch.setitem(sys.modules, "airflow.sdk.definitions", sdk_defs)
    monkeypatch.setitem(sys.modules, "airflow.sdk.definitions.context", sdk_ctx)
    monkeypatch.setitem(sys.modules, "airflow.models", models_mod)


"""TODO: Add docstring."""

import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import boto3
import pandas as pd
from moto import mock_aws

from imednet.integrations import export as export_mod


def test_export_to_csv(tmp_path, monkeypatch):
    """TODO: Add docstring."""
    df = pd.DataFrame({"a": [1, 2]})
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(
        export_mod, "_record_mapper", MagicMock(return_value=MagicMock(return_value=mapper_inst))
    )

    out_csv = tmp_path / "out.csv"
    export_mod.export_to_csv(MagicMock(), "S", str(out_csv))

    read = pd.read_csv(out_csv)
    assert len(read) == 2


def test_export_to_sql(tmp_path, monkeypatch):
    """TODO: Add docstring."""
    df = pd.DataFrame({"a": [1, 2]})
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(
        export_mod, "_record_mapper", MagicMock(return_value=MagicMock(return_value=mapper_inst))
    )

    db_file = tmp_path / "db.sqlite"
    export_mod.export_to_sql(MagicMock(), "S", "t", f"sqlite:///{db_file}")

    import sqlalchemy as sa

    eng = sa.create_engine(f"sqlite:///{db_file}")
    result = pd.read_sql_table("t", eng)
    assert len(result) == 2


def test_imednet_export_operator(monkeypatch):
    """TODO: Add docstring."""
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]
    
    _setup_airflow(monkeypatch)

    import apache_airflow_providers_imednet.operators.export as export_ops
    from apache_airflow_providers_imednet import ImednetExportOperator

    sdk = MagicMock()
    hook = MagicMock(get_sdk_client=MagicMock(return_value=sdk))
    monkeypatch.setattr(export_ops, "ImednetHook", MagicMock(return_value=hook))
    monkeypatch.setattr(export_mod, "export_to_csv", MagicMock())

    op = ImednetExportOperator(task_id="t", study_key="S", output_path="p")
    result = op.execute({})

    export_mod.export_to_csv.assert_called_once_with(sdk, "S", "p")
    assert result == "p"
    sys.modules.pop("apache_airflow_providers_imednet", None)


def test_imednet_hook_returns_sdk(monkeypatch):
    """TODO: Add docstring."""
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]

    _setup_airflow(monkeypatch)
    import airflow.sdk.bases.hook as hooks_base
    
    conn = SimpleNamespace(
        login="KEY", password="SEC", extra_dejson={"base_url": "https://x"}
    )
    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_conn()

    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"
    assert sdk._client.base_url == "https://x"
    sys.modules.pop("apache_airflow_providers_imednet", None)
