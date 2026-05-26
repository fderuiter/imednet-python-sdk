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
)

# ---------------------------------------------------------------------------
# _redact_uri
# ---------------------------------------------------------------------------


class TestRedactUri:
    def test_redacts_user_and_password(self):
        userpass_uri = "mongodb://" + "user:pass" + "@localhost:27017/db"
        assert _redact_uri(userpass_uri) == "mongodb://***@localhost:27017/db"

    def test_redacts_user_only(self):
        assert _redact_uri("bolt://neo4j@localhost:7687") == "bolt://***@localhost:7687"

    def test_leaves_uri_without_userinfo_unchanged(self):
        uri = "neo4j+s://bolt.example.com"
        assert _redact_uri(uri) == uri

    def test_handles_empty_string(self):
        assert _redact_uri("") == ""


# ---------------------------------------------------------------------------
# _require_optional_dep
# ---------------------------------------------------------------------------


class TestRequireOptionalDep:
    def test_returns_module_when_installed(self):
        mod = _require_optional_dep("sys", "dummy")
        assert mod is sys

    def test_raises_import_error_when_missing(self, monkeypatch):
        def fake_import(name):
            raise ModuleNotFoundError(name=name)

        monkeypatch.setattr(sink_base_mod, "import_module", fake_import)
        with pytest.raises(ImportError, match="imednet\\[mypkg\\]"):
            _require_optional_dep("mypkg", "mypkg")

    def test_reraises_unrelated_module_not_found_error(self, monkeypatch):
        def fake_import(name):
            raise ModuleNotFoundError(name="some_other_missing_lib")

        monkeypatch.setattr(sink_base_mod, "import_module", fake_import)
        with pytest.raises(ModuleNotFoundError):
            _require_optional_dep("mypkg", "mypkg")


# ---------------------------------------------------------------------------
# SinkConfig
# ---------------------------------------------------------------------------


class TestSinkConfig:
    def test_defaults(self):
        cfg = SinkConfig()
        assert cfg.batch_size == 500
        assert cfg.max_retries == 3
        assert cfg.retry_backoff == 1.0
        assert cfg.idempotent is True
        assert cfg.extra == {}

    def test_custom_values(self):
        cfg = SinkConfig(batch_size=100, max_retries=0, idempotent=False)
        assert cfg.batch_size == 100
        assert cfg.max_retries == 0
        assert cfg.idempotent is False


# ---------------------------------------------------------------------------
# ExportSink (concrete stub for testing)
# ---------------------------------------------------------------------------


class _StubSink(ExportSink):
    """Minimal concrete sink for testing the base class."""

    def __init__(self, config=None):
        super().__init__(config)
        self.batches: list[tuple[list, str]] = []
        self.flushed = False
        self.closed = False

    def write_batch(self, records, *, batch_id: str) -> int:
        self.batches.append((list(records), batch_id))
        return len(records)

    def flush(self) -> None:
        self.flushed = True

    def close(self) -> None:
        self.closed = True


class TestExportSinkContextManager:
    def test_flush_and_close_called_on_clean_exit(self):
        sink = _StubSink()
        with sink as s:
            s.write_batch([1, 2, 3], batch_id="b1")
        assert sink.flushed
        assert sink.closed

    def test_close_called_on_exception(self):
        sink = _StubSink()
        with pytest.raises(ValueError):
            with sink:
                raise ValueError("oops")
        # flush is NOT called on exception; close IS
        assert not sink.flushed
        assert sink.closed

    def test_write_batch_records_returned(self):
        sink = _StubSink()
        result = sink.write_batch([10, 20], batch_id="b2")
        assert result == 2
        assert sink.batches[0] == ([10, 20], "b2")


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class TestExportErrors:
    def test_export_error_is_imednet_error(self):
        from imednet.errors import ImednetError

        assert issubclass(ExportError, ImednetError)

    def test_export_batch_error_carries_batch_id(self):
        err = ExportBatchError("failed", batch_id="STUDY/FORM/0")
        assert err.batch_id == "STUDY/FORM/0"
        assert "failed" in str(err)

    def test_export_configuration_error_is_export_error(self):
        assert issubclass(ExportConfigurationError, ExportError)

    def test_export_batch_error_is_export_error(self):
        assert issubclass(ExportBatchError, ExportError)


# ---------------------------------------------------------------------------
# Neo4jExportSink
# ---------------------------------------------------------------------------


def _fake_neo4j_module(fail_connect: bool = False) -> ModuleType:
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


class TestNeo4jExportSink:
    def test_connect_calls_verify_connectivity(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module()
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)

        from imednet.integrations.graph import Neo4jExportSink

        sink = Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "STUDY1")
        driver.verify_connectivity.assert_called_once()
        sink.close()

    def test_connect_raises_configuration_error_on_failure(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module(fail_connect=True)
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)

        from imednet.integrations.graph import Neo4jExportSink

        with pytest.raises(ExportConfigurationError, match="Cannot connect to Neo4j"):
            Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "STUDY1")

    def test_write_batch_returns_count(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module()
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)

        from imednet.integrations.graph import Neo4jExportSink

        records = [
            MagicMock(record_id=i, form_id=1, visit_id=1, subject_key="S1", record_data={})
            for i in range(5)
        ]
        with Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "STUDY1") as sink:
            count = sink.write_batch(records, batch_id="STUDY1/F1/0")
        assert count == 5

    def test_write_batch_empty_returns_zero(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module()
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)

        from imednet.integrations.graph import Neo4jExportSink

        with Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "STUDY1") as sink:
            count = sink.write_batch([], batch_id="STUDY1/F1/0")
        assert count == 0

    def test_write_batch_raises_after_retries_exhausted(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module()
        # Make session.run always fail
        driver.session.return_value.__enter__.return_value.run.side_effect = RuntimeError("db down")
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)
        monkeypatch.setattr(graph_mod.time, "sleep", lambda _: None)

        from imednet.integrations.graph import Neo4jExportSink, Neo4jSinkConfig

        cfg = Neo4jSinkConfig(max_retries=1, retry_backoff=0.0)
        sink = Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "S1", config=cfg)
        with pytest.raises(ExportBatchError, match="STUDY1/F1/0"):
            records = [
                MagicMock(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})
            ]
            sink.write_batch(records, batch_id="STUDY1/F1/0")
        sink.close()

    def test_close_is_idempotent(self, monkeypatch):
        import imednet.integrations.graph as graph_mod

        neo4j, driver = _fake_neo4j_module()
        monkeypatch.setattr(graph_mod, "_require_optional_dep", lambda *_: neo4j)

        from imednet.integrations.graph import Neo4jExportSink

        sink = Neo4jExportSink("bolt://localhost:7687", ("neo4j", "pass"), "S1")
        sink.close()
        sink.close()  # must not raise


# ---------------------------------------------------------------------------
# MongoDbExportSink
# ---------------------------------------------------------------------------


def _fake_pymongo_module(fail_connect: bool = False) -> ModuleType:
    pymongo = ModuleType("pymongo")
    client = MagicMock()
    if fail_connect:
        client.admin.command.side_effect = Exception("connection refused")
    collection = MagicMock()
    result = MagicMock()
    result.upserted_count = 2
    result.modified_count = 1
    collection.bulk_write.return_value = result
    result_insert = MagicMock()
    result_insert.inserted_ids = [1, 2, 3]
    collection.insert_many.return_value = result_insert
    inner = MagicMock(__getitem__=MagicMock(return_value=collection))
    client.__getitem__ = MagicMock(return_value=inner)
    pymongo.MongoClient = MagicMock(return_value=client)
    pymongo.UpdateOne = MagicMock(side_effect=lambda *a, **kw: MagicMock())
    return pymongo, client, collection


class TestMongoDbExportSink:
    def test_connect_raises_configuration_error_on_failure(self, monkeypatch):
        import imednet.integrations.document as doc_mod

        pymongo, client, collection = _fake_pymongo_module(fail_connect=True)
        monkeypatch.setattr(doc_mod, "_require_optional_dep", lambda *_: pymongo)

        from imednet.integrations.document import MongoDbExportSink

        with pytest.raises(ExportConfigurationError, match="Cannot connect to MongoDB"):
            MongoDbExportSink("mongodb://localhost:27017", "db", "col", "STUDY1")

    def test_write_batch_upsert_returns_count(self, monkeypatch):
        import imednet.integrations.document as doc_mod

        pymongo, client, collection = _fake_pymongo_module()
        monkeypatch.setattr(doc_mod, "_require_optional_dep", lambda *_: pymongo)

        from imednet.integrations.document import MongoDbExportSink

        records = [
            MagicMock(record_id=i, form_id=1, visit_id=1, subject_key="S1", record_data={})
            for i in range(3)
        ]
        with MongoDbExportSink("mongodb://localhost:27017", "db", "col", "STUDY1") as sink:
            count = sink.write_batch(records, batch_id="STUDY1/F1/0")
        # upserted_count=2 + modified_count=1 = 3
        assert count == 3

    def test_write_batch_empty_returns_zero(self, monkeypatch):
        import imednet.integrations.document as doc_mod

        pymongo, client, collection = _fake_pymongo_module()
        monkeypatch.setattr(doc_mod, "_require_optional_dep", lambda *_: pymongo)

        from imednet.integrations.document import MongoDbExportSink

        with MongoDbExportSink("mongodb://localhost:27017", "db", "col", "STUDY1") as sink:
            count = sink.write_batch([], batch_id="b0")
        assert count == 0

    def test_write_batch_raises_after_retries(self, monkeypatch):
        import imednet.integrations.document as doc_mod

        pymongo, client, collection = _fake_pymongo_module()
        collection.bulk_write.side_effect = RuntimeError("mongo down")
        monkeypatch.setattr(doc_mod, "_require_optional_dep", lambda *_: pymongo)
        monkeypatch.setattr(doc_mod.time, "sleep", lambda _: None)

        from imednet.integrations.document import MongoDbExportSink

        cfg = SinkConfig(max_retries=1, retry_backoff=0.0)
        with MongoDbExportSink("mongodb://localhost:27017", "db", "col", "S1", config=cfg) as sink:
            with pytest.raises(ExportBatchError, match="S1/F1/0"):
                records = [
                MagicMock(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})
            ]
                sink.write_batch(records, batch_id="S1/F1/0")

    def test_document_id_format(self):
        from imednet.integrations.document import _make_document_id

        assert _make_document_id("MYSTUDY", 42) == "MYSTUDY/42"

    def test_close_is_idempotent(self, monkeypatch):
        import imednet.integrations.document as doc_mod

        pymongo, client, collection = _fake_pymongo_module()
        monkeypatch.setattr(doc_mod, "_require_optional_dep", lambda *_: pymongo)

        from imednet.integrations.document import MongoDbExportSink

        sink = MongoDbExportSink("mongodb://localhost:27017", "db", "col", "S1")
        sink.close()
        sink.close()  # must not raise


# ---------------------------------------------------------------------------
# SnowflakeExportSink
# ---------------------------------------------------------------------------


def _fake_snowflake_module() -> ModuleType:
    sf = ModuleType("snowflake.connector")
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    sf.connect = MagicMock(return_value=conn)
    return sf, conn, cursor


def _fake_pyarrow_modules() -> tuple:
    pa = ModuleType("pyarrow")
    pq = ModuleType("pyarrow.parquet")
    table = MagicMock()
    pa.Table = MagicMock()
    pa.Table.from_pylist = MagicMock(return_value=table)
    pq.write_table = MagicMock()
    return pa, pq, table


class TestSnowflakeExportSink:
    def _make_sink(self, monkeypatch, *, tmp_path, fail_connect=False):
        import imednet.integrations.warehouse as wh_mod
        from imednet.integrations.warehouse import SnowflakeSinkConfig

        sf, conn, cursor = _fake_snowflake_module()
        if fail_connect:
            sf.connect.side_effect = Exception("auth error")
        pa, pq, table = _fake_pyarrow_modules()

        def fake_require(pkg, extras):
            if pkg == "snowflake.connector":
                return sf
            if pkg == "pyarrow":
                return pa
            if pkg == "pyarrow.parquet":
                return pq
            return MagicMock()

        monkeypatch.setattr(wh_mod, "_require_optional_dep", fake_require)

        cfg = SnowflakeSinkConfig(
            account="acct",
            user="user",
            **{"password": "secret"},
            database="DB",
            schema="PUBLIC",
            warehouse="WH",
            stage="STG",
            table="TBL",
            local_staging_dir=str(tmp_path),
        )
        return cfg, sf, conn, cursor, pq

    def test_connect_raises_configuration_error_on_failure(self, monkeypatch, tmp_path):
        import imednet.integrations.warehouse as wh_mod
        from imednet.integrations.warehouse import SnowflakeExportSink, SnowflakeSinkConfig

        sf, conn, cursor = _fake_snowflake_module()
        sf.connect.side_effect = Exception("auth failed")
        pa, pq, table = _fake_pyarrow_modules()

        def fake_require(pkg, extras):
            if pkg == "snowflake.connector":
                return sf
            return pa if "pyarrow" in pkg else MagicMock()

        monkeypatch.setattr(wh_mod, "_require_optional_dep", fake_require)

        cfg = SnowflakeSinkConfig(
            account="acct",
            user="user",
            **{"password": "secret"},
            database="DB",
            schema="PUBLIC",
            warehouse="WH",
            stage="STG",
            table="TBL",
            local_staging_dir=str(tmp_path),
        )
        with pytest.raises(ExportConfigurationError, match="Cannot connect to Snowflake"):
            SnowflakeExportSink(config=cfg)

    def test_raises_for_missing_required_config(self, monkeypatch, tmp_path):
        import imednet.integrations.warehouse as wh_mod
        from imednet.integrations.warehouse import SnowflakeExportSink, SnowflakeSinkConfig

        sf, conn, cursor = _fake_snowflake_module()
        monkeypatch.setattr(wh_mod, "_require_optional_dep", lambda *_: sf)

        # account is empty → should raise
        cfg = SnowflakeSinkConfig(local_staging_dir=str(tmp_path))
        with pytest.raises(ExportConfigurationError, match="missing required fields"):
            SnowflakeExportSink(config=cfg)

    def test_write_batch_calls_put_and_copy(self, monkeypatch, tmp_path):
        from imednet.integrations.warehouse import SnowflakeExportSink

        cfg, sf, conn, cursor, pq = self._make_sink(monkeypatch, tmp_path=tmp_path)
        sink = SnowflakeExportSink(config=cfg)
        records = [
            MagicMock(record_id=i, form_id=1, visit_id=1, subject_key="S", record_data={})
            for i in range(3)
        ]
        count = sink.write_batch(records, batch_id="S1/F1/0")
        assert count == 3
        # PUT and COPY INTO must both be called
        calls = [str(c) for c in cursor.execute.call_args_list]
        assert any("PUT" in c for c in calls)
        assert any("COPY INTO" in c for c in calls)
        sink.close()

    def test_write_batch_empty_returns_zero(self, monkeypatch, tmp_path):
        from imednet.integrations.warehouse import SnowflakeExportSink

        cfg, sf, conn, cursor, pq = self._make_sink(monkeypatch, tmp_path=tmp_path)
        sink = SnowflakeExportSink(config=cfg)
        assert sink.write_batch([], batch_id="b0") == 0
        sink.close()

    def test_write_batch_raises_after_retries(self, monkeypatch, tmp_path):
        import imednet.integrations.warehouse as wh_mod
        from imednet.integrations.warehouse import SnowflakeExportSink, SnowflakeSinkConfig

        sf, conn, cursor = _fake_snowflake_module()
        cursor.execute.side_effect = RuntimeError("network error")
        pa, pq, table = _fake_pyarrow_modules()

        def fake_require(pkg, extras):
            if pkg == "snowflake.connector":
                return sf
            if pkg == "pyarrow":
                return pa
            if pkg == "pyarrow.parquet":
                return pq
            return MagicMock()

        monkeypatch.setattr(wh_mod, "_require_optional_dep", fake_require)
        monkeypatch.setattr(wh_mod.time, "sleep", lambda _: None)

        cfg = SnowflakeSinkConfig(
            account="acct",
            user="user",
            **{"password": "secret"},
            database="DB",
            schema="PUBLIC",
            warehouse="WH",
            stage="STG",
            table="TBL",
            local_staging_dir=str(tmp_path),
            max_retries=1,
            retry_backoff=0.0,
        )
        sink = SnowflakeExportSink(config=cfg)
        records = [MagicMock(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})]
        with pytest.raises(ExportBatchError, match="S1/F1/0"):
            sink.write_batch(records, batch_id="S1/F1/0")
        sink.close()

    def test_manifest_appended(self, monkeypatch, tmp_path):
        import json

        from imednet.integrations.warehouse import SnowflakeExportSink, SnowflakeSinkConfig

        cfg_dict, sf, conn, cursor, pq = self._make_sink(monkeypatch, tmp_path=tmp_path)
        manifest = tmp_path / "manifest.jsonl"

        cfg = SnowflakeSinkConfig(
            account="acct",
            user="user",
            **{"password": "secret"},
            database="DB",
            schema="PUBLIC",
            warehouse="WH",
            stage="STG",
            table="TBL",
            local_staging_dir=str(tmp_path),
            manifest_path=str(manifest),
        )

        # re-apply monkeypatch with correct cfg
        import imednet.integrations.warehouse as wh_mod2

        sf2, conn2, cursor2 = _fake_snowflake_module()
        pa2, pq2, table2 = _fake_pyarrow_modules()

        def fake_require2(pkg, extras):
            if pkg == "snowflake.connector":
                return sf2
            if pkg == "pyarrow":
                return pa2
            if pkg == "pyarrow.parquet":
                return pq2
            return MagicMock()

        monkeypatch.setattr(wh_mod2, "_require_optional_dep", fake_require2)

        sink = SnowflakeExportSink(config=cfg)
        records = [MagicMock(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})]
        sink.write_batch(records, batch_id="STUDY/FORM/0")
        sink.close()

        assert manifest.exists()
        entry = json.loads(manifest.read_text().strip())
        assert entry["batch_id"] == "STUDY/FORM/0"
        assert entry["row_count"] == 1

    def test_close_is_idempotent(self, monkeypatch, tmp_path):
        from imednet.integrations.warehouse import SnowflakeExportSink

        cfg, sf, conn, cursor, pq = self._make_sink(monkeypatch, tmp_path=tmp_path)
        sink = SnowflakeExportSink(config=cfg)
        sink.close()
        sink.close()  # must not raise


# ---------------------------------------------------------------------------
# integrations/__init__.py re-exports
# ---------------------------------------------------------------------------


class TestIntegrationsReExports:
    def test_sink_config_importable_from_integrations(self):
        from imednet.integrations import SinkConfig as ImportedSinkConfig

        assert ImportedSinkConfig is SinkConfig

    def test_neo4j_sink_importable_from_integrations(self):
        from imednet.integrations import Neo4jExportSink

        assert Neo4jExportSink.__module__ == "imednet.integrations.graph"

    def test_mongodb_sink_importable_from_integrations(self):
        from imednet.integrations import MongoDbExportSink

        assert MongoDbExportSink.__module__ == "imednet.integrations.document"

    def test_snowflake_sink_importable_from_integrations(self):
        from imednet.integrations import SnowflakeExportSink

        assert SnowflakeExportSink.__module__ == "imednet.integrations.warehouse"
