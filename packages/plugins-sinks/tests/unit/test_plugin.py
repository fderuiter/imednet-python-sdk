from unittest.mock import Mock

import pytest
from imednet_sinks.plugin import SinksNamespace, create_sinks


def test_sinks_namespace_exports_mongodb_objects():
    sdk = Mock()
    namespace = create_sinks(sdk)

    from imednet_sinks.document import MongoDbExportSink, export_to_mongodb

    assert namespace.export_to_mongodb is export_to_mongodb
    assert namespace.MongoDbExportSink is MongoDbExportSink


def test_sinks_namespace_exports_neo4j_objects():
    sdk = Mock()
    namespace = create_sinks(sdk)

    from imednet_sinks.graph import Neo4jExportSink, Neo4jSinkConfig, export_to_neo4j

    assert namespace.export_to_neo4j is export_to_neo4j
    assert namespace.Neo4jSinkConfig is Neo4jSinkConfig
    assert namespace.Neo4jExportSink is Neo4jExportSink


def test_sinks_namespace_exports_snowflake_objects():
    sdk = Mock()
    namespace = create_sinks(sdk)

    from imednet_sinks.warehouse import (
        SnowflakeExportSink,
        SnowflakeSinkConfig,
        export_to_snowflake,
    )

    assert namespace.export_to_snowflake is export_to_snowflake
    assert namespace.SnowflakeSinkConfig is SnowflakeSinkConfig
    assert namespace.SnowflakeExportSink is SnowflakeExportSink
