"""Plugin module."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from imednet.spi.facade import AsyncImednetFacade, ImednetFacade


class SinksNamespace:
    """SinksNamespace implementation."""

    def __init__(self, sdk: Union["ImednetFacade", "AsyncImednetFacade"]):
        """Perform   init   operation."""
        self._sdk = sdk

    @property
    def export_to_mongodb(self) -> Any:
        """Perform export to mongodb operation."""
        from .document import export_to_mongodb

        return export_to_mongodb

    @property
    def MongoDbExportSink(self) -> Any:
        """Perform MongoDbExportSink operation."""
        from .document import MongoDbExportSink

        return MongoDbExportSink

    @property
    def export_to_neo4j(self) -> Any:
        """Perform export to neo4j operation."""
        from .graph import export_to_neo4j

        return export_to_neo4j

    @property
    def Neo4jSinkConfig(self) -> Any:
        """Perform Neo4jSinkConfig operation."""
        from .graph import Neo4jSinkConfig

        return Neo4jSinkConfig

    @property
    def Neo4jExportSink(self) -> Any:
        """Perform Neo4jExportSink operation."""
        from .graph import Neo4jExportSink

        return Neo4jExportSink

    @property
    def export_to_snowflake(self) -> Any:
        """Perform export to snowflake operation."""
        from .warehouse import export_to_snowflake

        return export_to_snowflake

    @property
    def SnowflakeSinkConfig(self) -> Any:
        """Perform SnowflakeSinkConfig operation."""
        from .warehouse import SnowflakeSinkConfig

        return SnowflakeSinkConfig

    @property
    def SnowflakeExportSink(self) -> Any:
        """Perform SnowflakeExportSink operation."""
        from .warehouse import SnowflakeExportSink

        return SnowflakeExportSink


def create_sinks(sdk: Union["ImednetFacade", "AsyncImednetFacade"]) -> SinksNamespace:
    """Perform create sinks operation."""
    return SinksNamespace(sdk)
