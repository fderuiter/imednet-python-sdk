from unittest.mock import MagicMock

from imednet_sinks.plugin import SinksNamespace, create_sinks


def test_plugin_sinks_namespace():
    mock_sdk = MagicMock()
    namespace = create_sinks(mock_sdk)

    assert isinstance(namespace, SinksNamespace)

    # We just access the properties to test they load successfully
    assert namespace.export_to_mongodb is not None
    assert namespace.MongoDbExportSink is not None
    assert namespace.export_to_neo4j is not None
    assert namespace.Neo4jSinkConfig is not None
    assert namespace.Neo4jExportSink is not None
    assert namespace.export_to_snowflake is not None
    assert namespace.SnowflakeSinkConfig is not None
    assert namespace.SnowflakeExportSink is not None
