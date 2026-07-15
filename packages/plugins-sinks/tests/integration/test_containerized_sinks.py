"""TODO: Add docstring."""

import logging
import os
from typing import List

import pytest
from imednet_sinks import (
    MongoDbExportSink,
    MongoDbSinkConfig,
    Neo4jExportSink,
    Neo4jSinkConfig,
    export_to_mongodb,
    export_to_neo4j,
)

pytestmark = pytest.mark.skipif(
    os.getenv("IMEDNET_TEST_CONTAINERS") != "1", reason="Requires IMEDNET_TEST_CONTAINERS=1"
)


class DriftError(Exception):
    """TODO: Add docstring."""

    pass


class DriftFailingHandler(logging.Handler):
    """TODO: Add docstring."""

    def emit(self, record):
        """TODO: Add docstring."""
        if record.levelno >= logging.WARNING and "Drift detected" in record.getMessage():
            raise DriftError(record.getMessage())


