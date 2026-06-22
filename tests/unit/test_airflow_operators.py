"""TODO: Add docstring."""
import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest


def _setup_airflow(monkeypatch):
    """TODO: Add docstring."""
    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")
    sensors_base = ModuleType("airflow.sensors.base")
    exc_mod = ModuleType("airflow.exceptions")
    s3_mod = ModuleType("airflow.providers.amazon.aws.hooks.s3")

    class DummyBaseHook:
        """TODO: Add docstring."""
        @classmethod
        def get_connection(cls, conn_id):
            """TODO: Add docstring."""
            raise NotImplementedError

    class DummyBaseOperator:
        """TODO: Add docstring."""
        template_fields = ()

        def __init__(self, *a, **kw):
            """TODO: Add docstring."""
            pass

    class DummySensorOperator:
        """TODO: Add docstring."""
        template_fields = ()

        def __init__(self, *a, **kw):
            """TODO: Add docstring."""
            pass

    hooks_base.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator
    sensors_base.BaseSensorOperator = DummySensorOperator

    class DummyAirflowError(Exception):
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    _setup_airflow(monkeypatch)
    import apache_airflow_providers_imednet.operators as ops

    return ops


def _import_sensors(monkeypatch):
    """TODO: Add docstring."""
    _setup_airflow(monkeypatch)
    import apache_airflow_providers_imednet.sensors as sensors

    return sensors


def _patch_basehook(monkeypatch, extras=None):
    """TODO: Add docstring."""
    conn = SimpleNamespace(login=None, password=None, extra_dejson=extras or {})
    import apache_airflow_providers_imednet.hooks as hook_mod

    monkeypatch.setattr(
        hook_mod.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )
    return conn


def test_job_sensor(monkeypatch):
    """TODO: Add docstring."""
    _setup_airflow(monkeypatch)
    import apache_airflow_providers_imednet.operators as ops
    import apache_airflow_providers_imednet.sensors as sensors

    importlib.reload(sensors)
    _patch_basehook(monkeypatch)
    sdk = MagicMock()
    job = MagicMock(state="COMPLETED")
    sdk.jobs.get.return_value = job
    hook_inst = MagicMock(get_conn=MagicMock(return_value=sdk))
    monkeypatch.setattr(sensors, "ImednetHook", MagicMock(return_value=hook_inst))

    sensor = sensors.ImednetJobSensor(task_id="t", study_key="S", batch_id="B")
    assert sensor.poke({}) is True
    sdk.jobs.get.assert_called_once_with("S", "B")
    sensors.ImednetHook.assert_called_once_with("imednet_default")
    hook_inst.get_conn.assert_called_once_with()

    job.state = "FAILED"
    with pytest.raises(ops.AirflowException):
        sensor.poke({})

    job.state = "RUNNING"
    assert sensor.poke({}) is False
