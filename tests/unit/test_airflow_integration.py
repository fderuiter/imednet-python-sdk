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


def test_export_operator_isolates_output_path(monkeypatch):
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
        isolate_output_path=True,
    )

    result = op.execute({"map_index": 7})

    export_mock.assert_called_once_with(sdk, "S", "/tmp/out__7.csv")
    assert result == "/tmp/out__7.csv"

    op_without_extension = airflow_mod.ImednetExportOperator(
        task_id="t2",
        study_key="S",
        output_path="/tmp/out",
        export_func="export_to_csv",
        isolate_output_path=True,
    )
    result_no_extension = op_without_extension.execute({})
    assert result_no_extension == "/tmp/out__single"

    op_multi_extension = airflow_mod.ImednetExportOperator(
        task_id="t3",
        study_key="S",
        output_path="/tmp/out.tar.gz",
        export_func="export_to_csv",
        isolate_output_path=True,
    )
    result_multi_extension = op_multi_extension.execute({"map_index": 3})
    assert result_multi_extension == "/tmp/out__3.tar.gz"

    op_non_mapped_sentinel = airflow_mod.ImednetExportOperator(
        task_id="t4",
        study_key="S",
        output_path="/tmp/out.csv",
        export_func="export_to_csv",
        isolate_output_path=True,
    )
    result_sentinel = op_non_mapped_sentinel.execute({"map_index": -1})
    assert result_sentinel == "/tmp/out__single.csv"


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


def test_imednet_hook_get_sdk_client_alias(monkeypatch):
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

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    sdk = hook.get_sdk_client()

    assert isinstance(sdk, sdk_mod.ImednetSDK)


def test_imednet_hook_discover_studies_primitive_payload(monkeypatch):
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

    sdk = MagicMock()
    sdk.studies.list.return_value = [
        {"study_key": "S1", "study_name": "Active Study", "active": True},
        {"study_key": "S2", "study_name": "Inactive Study", "status": "INACTIVE"},
    ]

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    monkeypatch.setattr(hook, "get_sdk_client", MagicMock(return_value=sdk))

    studies = hook.discover_studies()
    assert studies == [{"study_key": "S1", "study_name": "Active Study", "is_active": True}]
    assert all(isinstance(item["study_key"], str) for item in studies)

    requests = hook.build_export_requests(output_root="/tmp/exports")
    assert requests == [{"study_key": "S1", "output_path": "/tmp/exports/S1.csv"}]


def test_imednet_hook_resolved_connection_config_redacts(monkeypatch):
    _setup_airflow(monkeypatch)

    conn = MagicMock()
    conn.login = "KEYVALUE"
    conn.password = "SECVALUE"
    conn.extra_dejson = {"base_url": "https://example.com"}

    import airflow.hooks.base as hooks_base

    monkeypatch.setattr(
        hooks_base.BaseHook,
        "get_connection",
        classmethod(lambda cls, cid: conn),
    )

    from apache_airflow_providers_imednet.hooks import ImednetHook

    hook = ImednetHook()
    config = hook.resolved_connection_config()
    assert config["api_key"] == "***"
    assert config["security_key"] == "***"
    assert config["base_url"] == "https://example.com"

    conn.login = "ABCD"
    conn.password = "XYZ"
    short_config = hook.resolved_connection_config()
    assert short_config["api_key"] == "***"
    assert short_config["security_key"] == "***"
