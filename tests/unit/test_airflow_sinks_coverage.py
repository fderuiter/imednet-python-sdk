import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

def _setup_airflow(monkeypatch):
    airflow = ModuleType("airflow")
    hooks_pkg = ModuleType("airflow.hooks")
    hooks_base = ModuleType("airflow.hooks.base")
    models_mod = ModuleType("airflow.models")
    sensors_base = ModuleType("airflow.sensors.base")
    exc_mod = ModuleType("airflow.exceptions")

    class DummyBaseHook:
        @classmethod
        def get_connection(cls, conn_id):
            raise NotImplementedError

    class DummyBaseOperator:
        template_fields = ()
        def __init__(self, *a, **kw):
            pass

    hooks_base.BaseHook = DummyBaseHook
    models_mod.BaseOperator = DummyBaseOperator

    class DummyAirflowError(Exception):
        pass

    exc_mod.AirflowException = DummyAirflowError

    hooks_pkg.base = hooks_base
    airflow.hooks = hooks_pkg
    airflow.models = models_mod
    airflow.exceptions = exc_mod

    modules = {
        "airflow": airflow,
        "airflow.hooks": hooks_pkg,
        "airflow.hooks.base": hooks_base,
        "airflow.models": models_mod,
        "airflow.exceptions": exc_mod,
    }
    for name, mod in modules.items():
        monkeypatch.setitem(sys.modules, name, mod)

def test_export_operator_resolve_snowflake(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator

    op = ImednetExportOperator(task_id="t", study_key="123", destination="snowflake")
    config = MagicMock()
    with patch("imednet_sinks.SnowflakeExportSink._connect"):
        sink = op._resolve_sink(config)
        assert sink is not None
        assert type(sink).__name__ == "SnowflakeExportSink"

def test_export_operator_resolve_neo4j(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator

    op = ImednetExportOperator(task_id="t", study_key="123", destination="neo4j", export_kwargs={"uri": "x", "auth": ("a", "b")})
    config = MagicMock()
    with patch("imednet_sinks.Neo4jExportSink._connect"):
        sink = op._resolve_sink(config)
        assert sink is not None
        assert type(sink).__name__ == "Neo4jExportSink"

def test_export_operator_resolve_mongodb(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator

    op = ImednetExportOperator(task_id="t", study_key="123", destination="mongodb", export_kwargs={"uri": "x", "database": "d", "collection": "c"})
    config = MagicMock()
    with patch("imednet_sinks.MongoDbExportSink._connect"):
        sink = op._resolve_sink(config)
        assert sink is not None
        assert type(sink).__name__ == "MongoDbExportSink"

def test_export_operator_no_dest_uses_csv(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator
    import apache_airflow_providers_imednet.export as export_mod

    op = ImednetExportOperator(task_id="t", study_key="123")
    
    mock_sdk = MagicMock()
    op._get_sdk = MagicMock(return_value=mock_sdk)
    
    with patch.object(export_mod, "export_to_csv") as mock_csv:
        op.execute(None)
        mock_csv.assert_called_once()

def test_export_operator_custom_export_func(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator
    import apache_airflow_providers_imednet.export as export_mod

    def fake_export_func(*args, **kwargs):
        pass

    setattr(export_mod, "my_custom_func", fake_export_func)

    op = ImednetExportOperator(task_id="t", study_key="123", export_func="my_custom_func")
    mock_sdk = MagicMock()
    op._get_sdk = MagicMock(return_value=mock_sdk)
    
    with patch.object(export_mod, "my_custom_func") as mock_custom:
        op.execute(None)
        mock_custom.assert_called_once()

def test_export_operator_execute_with_sink(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator

    op = ImednetExportOperator(task_id="t", study_key="123", destination="mongodb", batch_size=2)
    mock_sdk = MagicMock()
    mock_sdk.records.list.return_value = ["rec1", "rec2", "rec3"]
    op._get_sdk = MagicMock(return_value=mock_sdk)

    # Mock the sink
    mock_sink = MagicMock()
    op._resolve_sink = MagicMock(return_value=mock_sink)

    with patch("apache_airflow_providers_imednet.operators.export.apply_quality_gate", return_value=["rec1", "rec2", "rec3"]):
        op.execute(None)

    assert mock_sink.__enter__.called
    assert mock_sink.__exit__.called
    assert mock_sink.write_batch.call_count == 2  # 3 records, batch_size=2 -> 2 batches

def test_export_operator_invalid_dest(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator
    from apache_airflow_providers_imednet._airflow_compat import AirflowException

    op = ImednetExportOperator(task_id="t", study_key="123", destination="invalid_dest")
    with pytest.raises(Exception) as exc_info:
        op.execute(None)
    assert "Unsupported export_func" in str(exc_info.value)

def test_export_operator_retries_and_fails(monkeypatch):
    _setup_airflow(monkeypatch)
    from apache_airflow_providers_imednet.operators.export import ImednetExportOperator
    import apache_airflow_providers_imednet.export as export_mod

    op = ImednetExportOperator(task_id="t", study_key="123", destination="csv", max_retries=1)
    mock_sdk = MagicMock()
    op._get_sdk = MagicMock(return_value=mock_sdk)
    
    with patch.object(export_mod, "export_to_csv", side_effect=Exception("API Error")):
        with patch("apache_airflow_providers_imednet.operators.export.time.sleep") as mock_sleep:
            with pytest.raises(Exception, match="API Error"):
                op.execute(None)
            assert mock_sleep.call_count == 1
