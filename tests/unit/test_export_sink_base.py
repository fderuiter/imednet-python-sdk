"""Unit tests for the export sink architecture (sink_base, graph, document, warehouse)."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest

import imednet.integrations.sink_base as sink_base_mod
from imednet.errors import ExportBatchError, ExportConfigurationError, ExportError
from imednet.integrations.sink_base import (
    ExportSink,
    SinkConfig,
    _redact_uri,
    _require_optional_dep,
    iter_batches,
)

# ---------------------------------------------------------------------------
# _redact_uri
# ---------------------------------------------------------------------------


class TestRedactUri:
    """Test suite for RedactUri."""

    def test_redacts_user_and_password(self):
        """Test that redacts user and password."""
        userpass_uri = "mongodb://" + "user:pass" + "@localhost:27017/db"
        assert _redact_uri(userpass_uri) == "mongodb://***@localhost:27017/db"

    def test_redacts_user_only(self):
        """Test that redacts user only."""
        assert _redact_uri("bolt://neo4j@localhost:7687") == "bolt://***@localhost:7687"

    def test_leaves_uri_without_userinfo_unchanged(self):
        """Test that leaves uri without userinfo unchanged."""
        uri = "neo4j+s://bolt.example.com"
        assert _redact_uri(uri) == uri

    def test_handles_empty_string(self):
        """Test that handles empty string."""
        assert _redact_uri("") == ""


# ---------------------------------------------------------------------------
# _require_optional_dep
# ---------------------------------------------------------------------------


class TestRequireOptionalDep:
    """Test suite for RequireOptionalDep."""

    def test_returns_module_when_installed(self):
        """Test that returns module when installed."""
        mod = _require_optional_dep("sys", "dummy")
        assert mod is sys

    def test_raises_import_error_when_missing(self, monkeypatch):
        """Test that raises import error when missing."""

        def fake_import(name):
            """Helper function to fake import."""
            raise ModuleNotFoundError(name=name)

        monkeypatch.setattr(sink_base_mod, "import_module", fake_import)
        with pytest.raises(ImportError, match="imednet\\[mypkg\\]"):
            _require_optional_dep("mypkg", "mypkg")

    def test_reraises_unrelated_module_not_found_error(self, monkeypatch):
        """Test that reraises unrelated module not found error."""

        def fake_import(name):
            """Helper function to fake import."""
            raise ModuleNotFoundError(name="some_other_missing_lib")

        monkeypatch.setattr(sink_base_mod, "import_module", fake_import)
        with pytest.raises(ModuleNotFoundError):
            _require_optional_dep("mypkg", "mypkg")


# ---------------------------------------------------------------------------
# SinkConfig
# ---------------------------------------------------------------------------


class TestSinkConfig:
    """Test suite for SinkConfig."""

    def test_defaults(self):
        """Test that defaults."""
        cfg = SinkConfig(study_key="MY_STUDY")
        assert cfg.batch_size == 500
        assert cfg.max_retries == 3
        assert cfg.retry_backoff == 1.0
        assert cfg.idempotent is True
        assert cfg.extra == {}

    def test_custom_values(self):
        """Test that custom values."""
        cfg = SinkConfig(study_key="MY_STUDY", batch_size=100, max_retries=0, idempotent=False)
        assert cfg.batch_size == 100
        assert cfg.max_retries == 0
        assert cfg.idempotent is False


class TestIterBatches:
    """Test suite for IterBatches."""

    def test_splits_sequence_by_batch_size(self):
        """Test that splits sequence by batch size."""
        batches = list(iter_batches([1, 2, 3, 4, 5], 2))
        assert batches == [[1, 2], [3, 4], [5]]

    def test_rejects_non_positive_batch_size(self):
        """Test that rejects non positive batch size."""
        with pytest.raises(ValueError, match="batch_size"):
            list(iter_batches([1, 2], 0))


# ---------------------------------------------------------------------------
# ExportSink (concrete stub for testing)
# ---------------------------------------------------------------------------


class _StubSink(ExportSink):
    """Minimal concrete sink for testing the base class."""

    def __init__(self, config=None):
        """Initialize the test object."""
        super().__init__(config)
        self.batches: list[tuple[list, str]] = []
        self.flushed = False
        self.closed = False

    def write_batch(self, records, *, batch_id: str) -> int:
        """Helper function to write batch."""
        self.batches.append((list(records), batch_id))
        return len(records)

    def flush(self) -> None:
        """Helper function to flush."""
        self.flushed = True

    def close(self) -> None:
        """Helper function to close."""
        self.closed = True


class TestExportSinkContextManager:
    """Test suite for ExportSinkContextManager."""

    def test_flush_and_close_called_on_clean_exit(self):
        """Test that flush and close called on clean exit."""
        sink = _StubSink()
        with sink as s:
            s.write_batch([1, 2, 3], batch_id="b1")
        assert sink.flushed
        assert sink.closed

    def test_close_called_on_exception(self):
        """Test that close called on exception."""
        sink = _StubSink()
        with pytest.raises(ValueError), sink:
            raise ValueError("oops")
        # flush is NOT called on exception; close IS
        assert not sink.flushed
        assert sink.closed

    def test_write_batch_records_returned(self):
        """Test that write batch records returned."""
        sink = _StubSink()
        result = sink.write_batch([10, 20], batch_id="b2")
        assert result == 2
        assert sink.batches[0] == ([10, 20], "b2")


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class TestExportErrors:
    """Test suite for ExportErrors."""

    def test_export_error_is_imednet_error(self):
        """Test that export error is imednet error."""
        from imednet.errors import ImednetError

        assert issubclass(ExportError, ImednetError)

    def test_export_batch_error_carries_batch_id(self):
        """Test that export batch error carries batch id."""
        err = ExportBatchError("failed", batch_id="STUDY/FORM/0")
        assert err.batch_id == "STUDY/FORM/0"
        assert "failed" in str(err)

    def test_export_configuration_error_is_export_error(self):
        """Test that export configuration error is export error."""
        assert issubclass(ExportConfigurationError, ExportError)

    def test_export_batch_error_is_export_error(self):
        """Test that export batch error is export error."""
        assert issubclass(ExportBatchError, ExportError)


# ---------------------------------------------------------------------------
# Neo4jExportSink
# ---------------------------------------------------------------------------


def _fake_neo4j_module(fail_connect: bool = False) -> ModuleType:
    """Helper function to  fake neo4j module."""
    neo4j = ModuleType("neo4j")
    driver = MagicMock()
    if fail_connect:
        driver.verify_connectivity.side_effect = Exception("unreachable")
    session_ctx = MagicMock()
    session_ctx.__enter__ = MagicMock(return_value=MagicMock())
    session_ctx.__exit__ = MagicMock(return_value=False)
    driver.session.return_value = session_ctx
    neo4j.GraphDatabase = MagicMock()
    neo4j.GraphDatabase.driver.return_value = driver
    return neo4j, driver
