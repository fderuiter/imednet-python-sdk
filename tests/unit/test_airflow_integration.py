from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


def _fake_airflow(monkeypatch):
    airflow_mod = ModuleType("airflow")
    hooks_mod = ModuleType("airflow.hooks")
    base_mod = ModuleType("airflow.hooks.base")

    connection = MagicMock()
    connection.login = "login"
    connection.password = "secret"
    connection.extra_dejson = {"base_url": "https://example.com"}

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, _):
            return connection

    base_mod.BaseHook = DummyBaseHook
    hooks_mod.base = base_mod
    airflow_mod.hooks = hooks_mod

    models_mod = ModuleType("airflow.models")

    class DummyBaseOperator:
        template_fields: tuple[str, ...] = ()

        def __init__(self, **_):
            pass

    models_mod.BaseOperator = DummyBaseOperator

    monkeypatch.setitem(sys.modules, "airflow", airflow_mod)
    monkeypatch.setitem(sys.modules, "airflow.hooks", hooks_mod)
    monkeypatch.setitem(sys.modules, "airflow.hooks.base", base_mod)
    monkeypatch.setitem(sys.modules, "airflow.models", models_mod)

    return connection


@pytest.fixture(autouse=True)
def airflow_stubs(monkeypatch):
    return _fake_airflow(monkeypatch)


def test_imednet_hook_returns_sdk(monkeypatch):
    import imednet.integrations.airflow as ia

    sdk_instance = MagicMock()
    monkeypatch.setattr(ia, "ImednetSDK", MagicMock(return_value=sdk_instance))

    hook = ia.ImednetHook()
    sdk = hook.get_conn()

    assert sdk is sdk_instance
    ia.ImednetSDK.assert_called_once_with(
        api_key="login", security_key="secret", base_url="https://example.com"
    )


def test_export_operator_uses_hook(monkeypatch):
    import imednet.integrations.airflow as ia

    sdk_instance = MagicMock()
    hook = MagicMock()
    hook.get_conn.return_value = sdk_instance
    monkeypatch.setattr(ia, "ImednetHook", MagicMock(return_value=hook))

    export = MagicMock()
    monkeypatch.setattr(ia, "export_records_csv", export)

    op = ia.ImednetExportOperator(
        task_id="t",
        study_key="STUDY",
        file_path="/tmp/out.csv",
        flatten=False,
    )

    result = op.execute({})

    assert result == "/tmp/out.csv"
    export.assert_called_once_with(sdk_instance, "STUDY", "/tmp/out.csv", flatten=False)
    hook.get_conn.assert_called_once()
