import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import boto3
import pandas as pd
from imednet.integrations import export as export_mod
from moto import mock_aws


def test_export_to_csv(tmp_path, monkeypatch):
    df = pd.DataFrame({"a": [1, 2]})
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))

    out_csv = tmp_path / "out.csv"
    export_mod.export_to_csv(MagicMock(), "S", str(out_csv))

    read = pd.read_csv(out_csv)
    assert len(read) == 2


def test_export_to_sql(tmp_path, monkeypatch):
    df = pd.DataFrame({"a": [1, 2]})
    mapper_inst = MagicMock(dataframe=MagicMock(return_value=df))
    monkeypatch.setattr(export_mod, "RecordMapper", MagicMock(return_value=mapper_inst))

    db_file = tmp_path / "db.sqlite"
    export_mod.export_to_sql(MagicMock(), "S", "t", f"sqlite:///{db_file}")

    import sqlalchemy as sa

    eng = sa.create_engine(f"sqlite:///{db_file}")
    result = pd.read_sql_table("t", eng)
    assert len(result) == 2


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


def test_imednet_hook_returns_sdk(monkeypatch):
    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            return SimpleNamespace(
                login="KEY", password="SEC", extra_dejson={"base_url": "https://x"}
            )

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

    from imednet.integrations.airflow import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_conn()

    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"
    assert sdk._client.base_url == "https://x"
    sys.modules.pop("imednet.integrations.airflow", None)


@mock_aws
def test_to_s3_operator_uploads(monkeypatch):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="bucket")

    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")
    providers_mod = ModuleType("airflow.providers")
    amazon_mod = ModuleType("airflow.providers.amazon")
    aws_mod = ModuleType("airflow.providers.amazon.aws")
    hooks_amazon = ModuleType("airflow.providers.amazon.aws.hooks")
    s3_mod = ModuleType("airflow.providers.amazon.aws.hooks.s3")
    sensors_pkg = ModuleType("airflow.sensors")
    sensors_base = ModuleType("airflow.sensors.base")
    exc_mod = ModuleType("airflow.exceptions")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            return SimpleNamespace(login="K", password="S", extra_dejson={})

    class DummyBaseOperator:
        template_fields = ()

        def __init__(self, **kwargs):
            pass

    class DummyAirflowException(Exception):
        pass

    class DummyS3Hook:
        def __init__(self, aws_conn_id: str = "aws_default") -> None:
            self.client = s3

        def load_string(self, data: str, key: str, bucket: str, replace: bool = True) -> None:
            self.client.put_object(Bucket=bucket, Key=key, Body=data)

    class DummySensorOperator:
        template_fields = ()

        def __init__(self, *a, **kw):
            pass

    hooks_base.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator
    s3_mod.S3Hook = DummyS3Hook
    sensors_base.BaseSensorOperator = DummySensorOperator
    exc_mod.AirflowException = DummyAirflowException

    hooks_pkg.base = hooks_base
    airflow.hooks = hooks_pkg
    airflow.models = models_mod
    airflow.providers = providers_mod
    providers_mod.amazon = amazon_mod
    amazon_mod.aws = aws_mod
    aws_mod.hooks = hooks_amazon
    hooks_amazon.s3 = s3_mod
    airflow.exceptions = exc_mod

    modules = {
        "airflow": airflow,
        "airflow.hooks": hooks_pkg,
        "airflow.hooks.base": hooks_base,
        "airflow.models": models_mod,
        "airflow.sensors": sensors_pkg,
        "airflow.sensors.base": sensors_base,
        "airflow.providers": providers_mod,
        "airflow.providers.amazon": amazon_mod,
        "airflow.providers.amazon.aws": aws_mod,
        "airflow.providers.amazon.aws.hooks": hooks_amazon,
        "airflow.providers.amazon.aws.hooks.s3": s3_mod,
        "airflow.exceptions": exc_mod,
    }
    for name, mod in modules.items():
        monkeypatch.setitem(sys.modules, name, mod)

    import importlib

    from imednet.airflow import operators as ops

    importlib.reload(ops)

    sdk = MagicMock()
    sdk.records.list.return_value = [SimpleNamespace(model_dump=lambda: {"id": 1})]
    monkeypatch.setattr(ops, "ImednetSDK", MagicMock(return_value=sdk))

    op = ops.ImednetToS3Operator(task_id="t", study_key="S", s3_bucket="bucket", s3_key="k")
    result = op.execute({})

    assert result == "k"
    body = s3.get_object(Bucket="bucket", Key="k")["Body"].read().decode()
    assert "id" in body
    sys.modules.pop("imednet.airflow.operators", None)
