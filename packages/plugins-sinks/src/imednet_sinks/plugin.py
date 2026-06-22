"""TODO: Add docstring."""

from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from imednet.spi.facade import AsyncImednetFacade, ImednetFacade


class SinksNamespace:
    """TODO: Add docstring."""

    def __init__(self, sdk: Union["ImednetFacade", "AsyncImednetFacade"]):
        """TODO: Add docstring."""
        self._sdk = sdk

    @property
    def export_to_mongodb(self) -> Any:
        """TODO: Add docstring."""
        from .document import export_to_mongodb

        return export_to_mongodb

    @property
    def MongoDbExportSink(self) -> Any:
        """TODO: Add docstring."""
        from .document import MongoDbExportSink

        return MongoDbExportSink

    @property
    def export_to_neo4j(self) -> Any:
        """TODO: Add docstring."""
        from .graph import export_to_neo4j

        return export_to_neo4j

    @property
    def Neo4jSinkConfig(self) -> Any:
        """TODO: Add docstring."""
        from .graph import Neo4jSinkConfig

        return Neo4jSinkConfig

    @property
    def Neo4jExportSink(self) -> Any:
        """TODO: Add docstring."""
        from .graph import Neo4jExportSink

        return Neo4jExportSink

    @property
    def export_to_snowflake(self) -> Any:
        """TODO: Add docstring."""
        from .warehouse import export_to_snowflake

        return export_to_snowflake

    @property
    def SnowflakeSinkConfig(self) -> Any:
        """TODO: Add docstring."""
        from .warehouse import SnowflakeSinkConfig

        return SnowflakeSinkConfig

    @property
    def SnowflakeExportSink(self) -> Any:
        """TODO: Add docstring."""
        from .warehouse import SnowflakeExportSink

        return SnowflakeExportSink


def create_sinks(sdk: Union["ImednetFacade", "AsyncImednetFacade"]) -> SinksNamespace:
    """TODO: Add docstring."""
    return SinksNamespace(sdk)
