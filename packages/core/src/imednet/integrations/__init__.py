"""Integration helpers for exporting study data."""

from .document import MongoDbExportSink
from .export import (
    export_to_csv,
    export_to_duckdb,
    export_to_duckdb_by_form,
    export_to_excel,
    export_to_json,
    export_to_long_sql,
    export_to_parquet,
    export_to_sql,
    export_to_sql_by_form,
)
from .graph import Neo4jExportSink, Neo4jSinkConfig
from .parquet import export_to_hive_parquet, hive_parquet_query
from .sink_base import ExportSink, SinkConfig, _redact_uri, _require_optional_dep
from .warehouse import SnowflakeExportSink, SnowflakeSinkConfig

__all__ = [
    # Tabular path
    "export_to_csv",
    "export_to_duckdb",
    "export_to_duckdb_by_form",
    "export_to_excel",
    "export_to_hive_parquet",
    "export_to_json",
    "export_to_long_sql",
    "export_to_parquet",
    "export_to_sql_by_form",
    "export_to_sql",
    "hive_parquet_query",
    # Shared sink base
    "SinkConfig",
    "ExportSink",
    "_redact_uri",
    "_require_optional_dep",
    # Structure-preserving sinks
    "Neo4jExportSink",
    "Neo4jSinkConfig",
    "MongoDbExportSink",
    # Warehouse sinks
    "SnowflakeExportSink",
    "SnowflakeSinkConfig",
]
