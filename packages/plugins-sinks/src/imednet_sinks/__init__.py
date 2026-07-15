"""Unified Sinks plugin for iMednet."""

from .document import MongoDbExportSink, MongoDbSinkConfig, export_to_mongodb
from .graph import Neo4jExportSink, Neo4jSinkConfig, export_to_neo4j
from .warehouse import SnowflakeExportSink, SnowflakeSinkConfig, export_to_snowflake

__all__ = [
    "MongoDbExportSink",
    "MongoDbSinkConfig",
    "Neo4jExportSink",
    "Neo4jSinkConfig",
    "SnowflakeExportSink",
    "SnowflakeSinkConfig",
    "export_to_mongodb",
    "export_to_neo4j",
    "export_to_snowflake",
]
