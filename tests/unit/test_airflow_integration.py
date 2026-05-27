import sys
from datetime import datetime, timezone
from types import ModuleType
from unittest.mock import MagicMock

import pytest

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

    import apache_airflow_providers_imednet as airflow_mod

    hook = airflow_mod.ImednetHook()
    sdk = hook.get_conn()

    assert isinstance(sdk, sdk_mod.ImednetSDK)
    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"
    assert sdk._client.base_url == "https://example.com"


def test_export_operator_calls_helper(monkeypatch):
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]

    _setup_airflow(monkeypatch)

    conn = MagicMock()
    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    sdk = MagicMock()
    hook_inst = MagicMock(get_sdk_client=MagicMock(return_value=sdk))

    import apache_airflow_providers_imednet as airflow_mod
    import apache_airflow_providers_imednet.operators.export as export_ops

    monkeypatch.setattr(export_ops, "ImednetHook", MagicMock(return_value=hook_inst))
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


def test_export_operator_exposes_mapped_runtime_fields(monkeypatch):
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]

    _setup_airflow(monkeypatch)

    from apache_airflow_providers_imednet import ImednetExportOperator

    assert ImednetExportOperator.mapped_runtime_fields == (
        "study_key",
        "output_path",
        "export_kwargs",
    )
    assert ImednetExportOperator.template_fields == ImednetExportOperator.mapped_runtime_fields
    assert ImednetExportOperator.template_fields_renderers == {"export_kwargs": "json"}


def test_export_operator_copies_runtime_kwargs_and_resolves_sdk_at_execute(monkeypatch):
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]

    _setup_airflow(monkeypatch)

    conn = MagicMock()
    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    sdk = MagicMock()
    hook_inst = MagicMock(get_sdk_client=MagicMock(return_value=sdk))

    import apache_airflow_providers_imednet as airflow_mod
    import apache_airflow_providers_imednet.operators.export as export_ops

    hook_cls = MagicMock(return_value=hook_inst)
    monkeypatch.setattr(export_ops, "ImednetHook", hook_cls)
    export_mock = MagicMock()
    monkeypatch.setattr(airflow_mod.export, "export_to_json", export_mock)

    export_kwargs = {"orient": "records"}
    op = airflow_mod.ImednetExportOperator(
        task_id="t",
        study_key="S",
        output_path="/tmp/out.json",
        export_func="export_to_json",
        export_kwargs=export_kwargs,
    )

    export_kwargs["orient"] = "split"
    result = op.execute({})

    hook_cls.assert_called_once_with("imednet_default")
    hook_inst.get_sdk_client.assert_called_once_with()
    export_mock.assert_called_once_with(sdk, "S", "/tmp/out.json", orient="records")
    assert result == "/tmp/out.json"


def test_export_operator_rejects_unknown_export_callable(monkeypatch):
    if "apache_airflow_providers_imednet" in sys.modules:
        del sys.modules["apache_airflow_providers_imednet"]

    _setup_airflow(monkeypatch)

    conn = MagicMock()
    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet import ImednetExportOperator
    from apache_airflow_providers_imednet._airflow_compat import AirflowException

    op = ImednetExportOperator(
        task_id="t",
        study_key="S",
        output_path="/tmp/out.csv",
        export_func="does_not_exist",
    )

    with pytest.raises(AirflowException, match="Unsupported export_func"):
        op.execute({})


def test_imednet_hook_non_dict_extras(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = "KEY"
    conn.password = "SEC"
    conn.extra_dejson = "not-a-dict"

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_conn()

    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"


def test_imednet_hook_non_string_login(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = 123
    conn.password = "SEC"
    conn.extra_dejson = {"base_url": "https://example.com", "api_key": "FALLBACK_KEY"}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_conn()
    assert sdk._client._client.headers["x-api-key"] == "FALLBACK_KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "SEC"


def test_imednet_hook_non_string_password(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = "KEY"
    conn.password = 123
    conn.extra_dejson = {
        "base_url": "https://example.com",
        "security_key": "FALLBACK_SEC",
    }

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_conn()
    assert sdk._client._client.headers["x-api-key"] == "KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "FALLBACK_SEC"


def test_imednet_hook_environment_fallback(monkeypatch):
    _setup_airflow(monkeypatch)
    monkeypatch.setenv("IMEDNET_API_KEY", "ENV_KEY")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "ENV_SEC")

    conn = MagicMock()
    conn.login = None
    conn.password = None
    # Intentionally invalid non-string extras to verify env fallback normalization.
    conn.extra_dejson = {"api_key": 123, "security_key": object(), "base_url": 456}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_sdk_client()
    assert sdk._client._client.headers["x-api-key"] == "ENV_KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "ENV_SEC"
    assert sdk._client.base_url != "456"


def test_imednet_hook_describe_connection_redacts_credentials(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = "KEY"
    conn.password = "SEC"
    conn.extra_dejson = {"base_url": "https://example.com", "api_key": "EXTRA_KEY"}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook("imednet_custom")
    metadata = hook.describe_connection()

    assert metadata == {
        "imednet_conn_id": "imednet_custom",
        "base_url": "https://example.com",
        "api_key": "***",
        "security_key": "***",
        "api_key_configured": True,
        "security_key_configured": True,
    }


def test_imednet_hook_prefers_extras_over_environment(monkeypatch):
    _setup_airflow(monkeypatch)
    monkeypatch.setenv("IMEDNET_API_KEY", "ENV_KEY")
    monkeypatch.setenv("IMEDNET_SECURITY_KEY", "ENV_SEC")

    conn = MagicMock()
    conn.login = "LOGIN_KEY"
    conn.password = "LOGIN_SEC"
    conn.extra_dejson = {"api_key": "EXTRA_KEY", "security_key": "EXTRA_SEC"}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_sdk_client()
    assert sdk._client._client.headers["x-api-key"] == "EXTRA_KEY"
    assert sdk._client._client.headers["x-imn-security-key"] == "EXTRA_SEC"


def test_imednet_hook_study_discovery_serialization_safe(monkeypatch):
    _setup_airflow(monkeypatch)

    from apache_airflow_providers_imednet.hooks import ImednetHook

    class _StudyModel:
        def model_dump(self, mode="json", by_alias=True):
            assert mode == "json"
            assert by_alias is True
            return {
                "studyKey": "S-001",
                "dateModified": datetime(2025, 1, 1, tzinfo=timezone.utc),
                "api_key": "SECRET",
                "flags": ("a", "b"),
            }

    sdk = MagicMock()
    sdk.studies.list.return_value = [_StudyModel()]

    hook = ImednetHook()
    monkeypatch.setattr(hook, "get_sdk_client", MagicMock(return_value=sdk))

    metadata = hook.list_studies_metadata()
    keys = hook.list_study_keys()

    assert metadata == [
        {
            "studyKey": "S-001",
            "dateModified": "2025-01-01T00:00:00+00:00",
            "api_key": "***",
            "flags": ["a", "b"],
        }
    ]
    assert keys == ["S-001"]
