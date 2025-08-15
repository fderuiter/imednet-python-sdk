import sys
from types import ModuleType

import pytest


def _setup_airflow(monkeypatch):
    airflow_mod = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_mod = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):  # pragma: no cover
            raise NotImplementedError

    class DummyBaseOperator:
        template_fields = ()

        def __init__(self, **kwargs):  # pragma: no cover
            pass

    hooks_mod.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator

    hooks_pkg.base = hooks_mod
    airflow_mod.hooks = hooks_pkg
    airflow_mod.models = models_mod

    monkeypatch.setitem(sys.modules, "airflow", airflow_mod)
    monkeypatch.setitem(sys.modules, "airflow.hooks", hooks_pkg)
    monkeypatch.setitem(sys.modules, "airflow.hooks.base", hooks_mod)
    monkeypatch.setitem(sys.modules, "airflow.models", models_mod)


def test_airflow_shim_warns_and_re_exports(monkeypatch):
    _setup_airflow(monkeypatch)
    for mod in [
        "imednet.airflow",
        "imednet.integrations.airflow",
        "imednet.integrations.airflow.hooks",
        "imednet.integrations.airflow.operators",
        "imednet.integrations.airflow.sensors",
    ]:
        monkeypatch.delitem(sys.modules, mod, raising=False)

    with pytest.warns(DeprecationWarning):
        import imednet.airflow as shim

    from imednet.integrations import airflow as new

    assert shim.ImednetHook is new.ImednetHook
    assert shim.ImednetJobSensor is new.ImednetJobSensor
    assert shim.ImednetExportOperator is new.ImednetExportOperator
    assert shim.ImednetToS3Operator is new.ImednetToS3Operator
