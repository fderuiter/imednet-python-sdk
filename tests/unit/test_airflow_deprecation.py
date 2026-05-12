import sys
from types import ModuleType


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


def test_airflow_provider_exports_public_api(monkeypatch):
    _setup_airflow(monkeypatch)
    for mod in [
        "apache_airflow_providers_imednet",
        "apache_airflow_providers_imednet.hooks",
        "apache_airflow_providers_imednet.operators",
        "apache_airflow_providers_imednet.sensors",
    ]:
        monkeypatch.delitem(sys.modules, mod, raising=False)

    import apache_airflow_providers_imednet as provider

    assert provider.ImednetHook is not None
    assert provider.ImednetExportOperator is not None
    assert provider.ImednetToS3Operator is not None
