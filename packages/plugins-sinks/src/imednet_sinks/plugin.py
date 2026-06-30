"""Entry point for the iMednet sinks plugin.

This module provides the :class:`SinksNamespace` which aggregates all available
data export sinks (MongoDB, Neo4j, Snowflake) under a single namespace on the
SDK instance.
"""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from imednet.spi.facade import AsyncImednetFacade, ImednetFacade


class SinksNamespace:
    """Namespace for accessing data export sinks.

    This class is typically instantiated by the SDK and exposed via
    ``sdk.sinks``. It provides properties to access sink-specific export
    functions and class definitions.
    """

    def __init__(self, sdk: Union["ImednetFacade", "AsyncImednetFacade"]):
        """Initialize the sinks namespace.

        Args:
            sdk: An instance of the iMednet SDK (synchronous or asynchronous).
        """
        self._sdk = sdk

    @property
    def export_to_mongodb(self) -> Any:
        """Helper function to export records to MongoDB."""
        from .document import export_to_mongodb

        return export_to_mongodb

    @property
    def MongoDbExportSink(self) -> Any:
        """Sink class for exporting records to MongoDB."""
        from .document import MongoDbExportSink

        return MongoDbExportSink

    @property
    def export_to_neo4j(self) -> Any:
        """Helper function to export records to Neo4j."""
        from .graph import export_to_neo4j

        return export_to_neo4j

    @property
    def Neo4jSinkConfig(self) -> Any:
        """Configuration class for Neo4j sinks."""
        from .graph import Neo4jSinkConfig

        return Neo4jSinkConfig

    @property
    def Neo4jExportSink(self) -> Any:
        """Sink class for exporting records to Neo4j."""
        from .graph import Neo4jExportSink

        return Neo4jExportSink

    @property
    def export_to_snowflake(self) -> Any:
        """Helper function to export records to Snowflake."""
        from .warehouse import export_to_snowflake

        return export_to_snowflake

    @property
    def SnowflakeSinkConfig(self) -> Any:
        """Configuration class for Snowflake sinks."""
        from .warehouse import SnowflakeSinkConfig

        return SnowflakeSinkConfig

    @property
    def SnowflakeExportSink(self) -> Any:
        """Sink class for exporting records to Snowflake."""
        from .warehouse import SnowflakeExportSink

        return SnowflakeExportSink


def create_sinks(sdk: Union["ImednetFacade", "AsyncImednetFacade"]) -> SinksNamespace:
    """Factory function to create a new SinksNamespace instance."""
    return SinksNamespace(sdk)
