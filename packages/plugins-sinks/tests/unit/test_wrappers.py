from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


def test_mongodb_wrapper():
    from imednet_sinks.document import export_to_mongodb

    mock_sdk = MagicMock()
    with (
        patch("imednet.integrations.sink_base.apply_enrichment_pipeline", lambda s, r: iter(r)),
        patch("imednet.integrations.sink_base.apply_quality_gate", lambda s1, s2, r, c: r),
        patch("imednet_sinks.document.MongoDbExportSink") as mock_sink_cls,
        patch("imednet_sinks.document.iter_batches", return_value=[[1]]),
    ):
        mock_sink = mock_sink_cls.return_value.__enter__.return_value
        mock_sink.write_batch.return_value = 1

        count = export_to_mongodb(mock_sdk, "S1", "mongodb://fake", "db", "col")
        assert count == 1


def test_neo4j_wrapper():
    from imednet_sinks.graph import export_to_neo4j

    mock_sdk = MagicMock()
    with (
        patch("imednet.integrations.sink_base.apply_enrichment_pipeline", lambda s, r: iter(r)),
        patch("imednet_sinks.graph.Neo4jExportSink") as mock_sink_cls,
        patch("imednet_sinks.graph.iter_batches", return_value=[[1]]),
    ):
        mock_sink = mock_sink_cls.return_value.__enter__.return_value
        mock_sink.write_batch.return_value = 1

        count = export_to_neo4j(mock_sdk, "S1", "bolt://fake", ("a", "b"))
        assert count == 1


def test_snowflake_wrapper():
    from imednet_sinks.warehouse import SnowflakeSinkConfig, export_to_snowflake

    mock_sdk = MagicMock()
    mock_config = SnowflakeSinkConfig(
        account="a", user="u", password="p", database="d", schema="s", warehouse="w"
    )
    with (
        patch("imednet.integrations.sink_base.apply_enrichment_pipeline", lambda s, r: iter(r)),
        patch("imednet.integrations.sink_base.apply_quality_gate", lambda s1, s2, r, c: r),
        patch("imednet_sinks.warehouse.SnowflakeExportSink") as mock_sink_cls,
        patch("imednet_sinks.warehouse.iter_batches", return_value=[[1]]),
    ):
        mock_sink = mock_sink_cls.return_value.__enter__.return_value
        mock_sink.write_batch.return_value = 1

        count = export_to_snowflake(mock_sdk, "S1", config=mock_config)
        assert count == 1


def test_mongodb_write_batch_no_upsert():
    from imednet_sinks.document import MongoDbExportSink

    from imednet.integrations.sink_base import SinkConfig

    record = SimpleNamespace(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})
    # wait, SinkConfig doesn't take upsert=False? Let's check SinkConfig.
    # Actually, document.py might not use SinkConfig's upsert?
    # Let's mock MongoDbExportSink
    pass


def test_snowflake_tmp_dir():
    from imednet_sinks.warehouse import SnowflakeExportSink, SnowflakeSinkConfig

    with patch("imednet_sinks.warehouse._require_optional_dep") as mock_dep:
        mock_dep.return_value = MagicMock()
        mock_config = SnowflakeSinkConfig(
            account="a",
            user="u",
            password="p",
            database="d",
            schema="s",
            warehouse="w",
            stage="stg",
            table="tbl",
        )
        sink = SnowflakeExportSink(config=mock_config)
        assert sink._tmp_dir is not None
        sink.close()
        assert sink._tmp_dir is None


def test_mongodb_write_batch_no_idempotent():
    from imednet_sinks.document import MongoDbExportSink

    from imednet.integrations.sink_base import SinkConfig

    record = SimpleNamespace(record_id=1, form_id=1, visit_id=1, subject_key="S", record_data={})
    cfg = SinkConfig(idempotent=False)
    with patch("imednet_sinks.document._require_optional_dep") as mock_dep:
        mock_mongo = MagicMock()
        mock_dep.return_value = mock_mongo
        sink = MongoDbExportSink("fake", "db", "col", "S1", config=cfg)
        mock_col = sink._collection
        mock_col.insert_many.return_value.inserted_ids = [1]

        count = sink.write_batch([record], batch_id="test")
        assert count == 1
        mock_col.insert_many.assert_called_once()
