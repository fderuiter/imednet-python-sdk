import sys
from types import ModuleType
from unittest.mock import MagicMock

import imednet.sdk as sdk_mod


def _setup_airflow(monkeypatch):
    airflow_mod = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_mod = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            raise NotImplementedError

    class DummyBaseOperator:
        template_fields = ()

        def __init__(self, **kwargs):
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


def test_imednet_hook_returns_sdk(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = "KEY"
    conn.password = "SEC"
    conn.extra_dejson = {"base_url": "https://example.com"}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    import imednet.integrations.airflow as airflow_mod

    hook = airflow_mod.ImednetHook()
    sdk = hook.get_conn()

    assert isinstance(sdk, sdk_mod.ImednetSDK)
    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"
    assert sdk._client.base_url == "https://example.com"


def test_export_operator_calls_helper(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    sdk = MagicMock()
    hook_inst = MagicMock(get_conn=MagicMock(return_value=sdk))

    import imednet.integrations.airflow as airflow_mod

    monkeypatch.setattr(airflow_mod, "ImednetHook", MagicMock(return_value=hook_inst))
    export_mock = MagicMock()
    monkeypatch.setattr(airflow_mod.export, "export_to_csv", export_mock)

    op = airflow_mod.ImednetExportOperator(
        task_id="t",
        study_key="S",
        output_path="/tmp/out.csv",
        export_func="export_to_csv",
    )

    result = op.execute({})

    export_mock.assert_called_once_with(sdk, "S", "/tmp/out.csv")
    assert result == "/tmp/out.csv"
