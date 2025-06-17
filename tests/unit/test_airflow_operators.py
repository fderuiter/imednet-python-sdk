import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest


def _setup_airflow(monkeypatch):
    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")
    sensors_base = ModuleType("airflow.sensors.base")
    exc_mod = ModuleType("airflow.exceptions")
    s3_mod = ModuleType("airflow.providers.amazon.aws.hooks.s3")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            raise NotImplementedError

    class DummyBaseOperator:
        template_fields = ()

        def __init__(self, *a, **kw):
            pass

    class DummySensorOperator:
        template_fields = ()

        def __init__(self, *a, **kw):
            pass

    hooks_base.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator
    sensors_base.BaseSensorOperator = DummySensorOperator

    class DummyAirflowError(Exception):
        pass

    exc_mod.AirflowException = DummyAirflowError
    s3_mod.S3Hook = MagicMock

    hooks_pkg.base = hooks_base
    airflow.hooks = hooks_pkg
    airflow.models = models_mod
    airflow.sensors = ModuleType("airflow.sensors")
    airflow.sensors.base = sensors_base
    airflow.providers = ModuleType("airflow.providers")
    airflow.providers.amazon = ModuleType("airflow.providers.amazon")
    airflow.providers.amazon.aws = ModuleType("airflow.providers.amazon.aws")
    airflow.providers.amazon.aws.hooks = ModuleType("airflow.providers.amazon.aws.hooks")
    airflow.providers.amazon.aws.hooks.s3 = s3_mod

    modules = {
        "airflow": airflow,
        "airflow.hooks": hooks_pkg,
        "airflow.hooks.base": hooks_base,
        "airflow.models": models_mod,
        "airflow.sensors": airflow.sensors,
        "airflow.sensors.base": sensors_base,
        "airflow.providers": airflow.providers,
        "airflow.providers.amazon": airflow.providers.amazon,
        "airflow.providers.amazon.aws": airflow.providers.amazon.aws,
        "airflow.providers.amazon.aws.hooks": airflow.providers.amazon.aws.hooks,
        "airflow.providers.amazon.aws.hooks.s3": s3_mod,
        "airflow.exceptions": exc_mod,
    }
    for name, mod in modules.items():
        monkeypatch.setitem(sys.modules, name, mod)


def _import_operators(monkeypatch):
    _setup_airflow(monkeypatch)
    import imednet.integrations.airflow.operators as ops

    importlib.reload(ops)
    return ops


def _patch_basehook(monkeypatch, operators, extras=None):
    conn = SimpleNamespace(login=None, password=None, extra_dejson=extras or {})
    monkeypatch.setattr(
        operators.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )
    return conn


def _patch_s3(monkeypatch, operators):
    hook = MagicMock(load_string=MagicMock())
    monkeypatch.setattr(operators, "S3Hook", MagicMock(return_value=hook))
    return hook


def test_to_s3_operator_success(monkeypatch):
    ops = _import_operators(monkeypatch)
    _patch_basehook(monkeypatch, ops, {"api_key": "A", "security_key": "B"})
    hook = _patch_s3(monkeypatch, ops)
    sdk = MagicMock()
    sdk.records.list.return_value = [SimpleNamespace(model_dump=lambda: {"id": 1})]
    monkeypatch.setattr(ops, "ImednetSDK", MagicMock(return_value=sdk))

    op = ops.ImednetToS3Operator(task_id="t", study_key="S", s3_bucket="B", s3_key="k")
    result = op.execute({})

    assert result == "k"
    sdk.records.list.assert_called_once_with("S")
    hook.load_string.assert_called_once()


def test_to_s3_operator_missing_list(monkeypatch):
    ops = _import_operators(monkeypatch)
    _patch_basehook(monkeypatch, ops)
    _patch_s3(monkeypatch, ops)
    sdk = MagicMock()
    sdk.bad = object()
    monkeypatch.setattr(ops, "ImednetSDK", MagicMock(return_value=sdk))

    op = ops.ImednetToS3Operator(
        task_id="t", study_key="S", s3_bucket="B", s3_key="k", endpoint="bad"
    )
    with pytest.raises(ops.AirflowException):
        op.execute({})


def test_job_sensor(monkeypatch):
    ops = _import_operators(monkeypatch)
    _patch_basehook(monkeypatch, ops)
    sdk = MagicMock()
    job = MagicMock(state="COMPLETED")
    sdk.jobs.get.return_value = job
    monkeypatch.setattr(ops, "ImednetSDK", MagicMock(return_value=sdk))

    sensor = ops.ImednetJobSensor(task_id="t", study_key="S", batch_id="B")
    assert sensor.poke({}) is True
    sdk.jobs.get.assert_called_once_with("S", "B")

    job.state = "FAILED"
    with pytest.raises(ops.AirflowException):
        sensor.poke({})

    job.state = "RUNNING"
    assert sensor.poke({}) is False
