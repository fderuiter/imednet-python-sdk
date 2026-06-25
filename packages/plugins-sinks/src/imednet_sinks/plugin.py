"""Plugin module."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from imednet.spi.facade import AsyncImednetFacade, ImednetFacade


class SinksNamespace:
    """Implementation of the SinksNamespace class."""

    def __init__(self, sdk: Union["ImednetFacade", "AsyncImednetFacade"]):
        """Initialize a new instance."""
        self._sdk = sdk

    @property
    def export_to_mongodb(self) -> Any:
        """Handle the export to mongodb process."""
        from .document import export_to_mongodb

        return export_to_mongodb

    @property
    def MongoDbExportSink(self) -> Any:
        """Handle the MongoDbExportSink process."""
        from .document import MongoDbExportSink

        return MongoDbExportSink

    @property
    def export_to_neo4j(self) -> Any:
        """Handle the export to neo4j process."""
        from .graph import export_to_neo4j

        return export_to_neo4j

    @property
    def Neo4jSinkConfig(self) -> Any:
        """Handle the Neo4jSinkConfig process."""
        from .graph import Neo4jSinkConfig

        return Neo4jSinkConfig

    @property
    def Neo4jExportSink(self) -> Any:
        """Handle the Neo4jExportSink process."""
        from .graph import Neo4jExportSink

        return Neo4jExportSink

    @property
    def export_to_snowflake(self) -> Any:
        """Handle the export to snowflake process."""
        from .warehouse import export_to_snowflake

        return export_to_snowflake

    @property
    def SnowflakeSinkConfig(self) -> Any:
        """Handle the SnowflakeSinkConfig process."""
        from .warehouse import SnowflakeSinkConfig

        return SnowflakeSinkConfig

    @property
    def SnowflakeExportSink(self) -> Any:
        """Handle the SnowflakeExportSink process."""
        from .warehouse import SnowflakeExportSink

        return SnowflakeExportSink


def create_sinks(sdk: Union["ImednetFacade", "AsyncImednetFacade"]) -> SinksNamespace:
    """Handle the create sinks process."""
    return SinksNamespace(sdk)
