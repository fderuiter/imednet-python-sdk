"""Unit tests for the export dispatcher and registry."""

from unittest.mock import MagicMock, patch

import pytest

from imednet.integrations.dispatcher import export, register_sink_target, register_tabular_target
from imednet.integrations.sink_base import ExportSink, SinkConfig


class DummySink(ExportSink):
    """A dummy sink for testing routing and lifecycle management."""

    def __init__(self, config=None, **kwargs):
        """Initialize the dummy sink."""
        super().__init__(config)
        self.kwargs = kwargs
        self.written_batches = 0
        self.flushed = False
        self.closed = False

    def write_batch(self, records, *, batch_id):
        """Mock write_batch."""
        self.written_batches += len(records)
        return len(records)

    def flush(self):
        """Mock flush."""
        self.flushed = True

    def close(self):
        """Mock close."""
        self.closed = True


def dummy_tabular(sdk, study_key, **kwargs):
    """A dummy tabular function for testing."""
    return {"tabular": True, "sdk": sdk, "study_key": study_key, "kwargs": kwargs}


def test_export_tabular_routing():
    """Test that export correctly routes to a registered tabular function."""
    register_tabular_target("dummy_tab", dummy_tabular)

    sdk_mock = MagicMock()
    result = export("dummy_tab", sdk_mock, "STUDY1", my_arg="value")

    assert result["tabular"] is True
    assert result["sdk"] is sdk_mock
    assert result["study_key"] == "STUDY1"
    assert result["kwargs"] == {"my_arg": "value"}


@patch("imednet.integrations.dispatcher.iter_batches")
@patch("imednet.integrations.dispatcher.apply_quality_gate")
def test_export_sink_routing(mock_quality_gate, mock_iter_batches):
    """Test that export correctly routes to a registered sink class and handles lifecycle."""
    register_sink_target("dummy_sink", DummySink)

    sdk_mock = MagicMock()
    # Mock records return
    sdk_mock.records.list.return_value = [{"id": 1}, {"id": 2}]
    mock_quality_gate.return_value = [{"id": 1}, {"id": 2}]
    mock_iter_batches.return_value = [[{"id": 1}], [{"id": 2}]]

    total = export("dummy_sink", sdk_mock, "STUDY2", extra_arg="test")

    assert total == 2
    mock_quality_gate.assert_called_once()
    mock_iter_batches.assert_called_once()


def test_export_unsupported_target():
    """Test that an unknown target raises a ValueError."""
    sdk_mock = MagicMock()
    with pytest.raises(ValueError, match="Unsupported export target: 'unknown_target'"):
        export("unknown_target", sdk_mock, "STUDY3")

def test_get_sink_lazy_load_success(monkeypatch):
    from imednet.integrations.dispatcher import ExportRegistry
    
    registry = ExportRegistry()
    registry._LAZY_SINKS = {"dummy_target": "dummy_module:DummyClass"}
    
    class DummyClass:
        pass

    class DummyModule:
        pass
    DummyModule.DummyClass = DummyClass

    # Mock importlib.import_module
    def mock_import(name):
        if name == "dummy_module":
            return DummyModule
        raise ImportError
        
    monkeypatch.setattr("importlib.import_module", mock_import)
    
    # Should lazily load and register
    sink = registry.get_sink("dummy_target")
    assert sink is DummyClass
    assert registry._sink_targets["dummy_target"] is DummyClass

def test_get_sink_lazy_load_import_error(monkeypatch):
    from imednet.integrations.dispatcher import ExportRegistry
    
    registry = ExportRegistry()
    registry._LAZY_SINKS = {"dummy_target": "dummy_module:DummyClass"}

    # Mock importlib.import_module to raise ImportError
    def mock_import(name):
        raise ImportError
        
    monkeypatch.setattr("importlib.import_module", mock_import)
    
    # Should handle ImportError and return None
    sink = registry.get_sink("dummy_target")
    assert sink is None

def test_get_sink_lazy_load_attribute_error(monkeypatch):
    from imednet.integrations.dispatcher import ExportRegistry
    
    registry = ExportRegistry()
    registry._LAZY_SINKS = {"dummy_target": "dummy_module:DummyClass"}

    class DummyModule:
        pass

    # Mock importlib.import_module
    def mock_import(name):
        return DummyModule
        
    monkeypatch.setattr("importlib.import_module", mock_import)
    
    # Should handle AttributeError (DummyClass not in DummyModule) and return None
    sink = registry.get_sink("dummy_target")
    assert sink is None
