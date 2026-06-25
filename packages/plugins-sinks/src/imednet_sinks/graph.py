"""Neo4j graph export sink.

This module implements the **structure-preserving export path** for a Neo4j
property-graph destination.  Records fetched via
:class:`~imednet_workflows.data_extraction.DataExtractionWorkflow` are written
as graph nodes and relationships that mirror the clinical data hierarchy.

Graph shape
-----------
Nodes
~~~~~
* ``(:Study   {study_key})``
* ``(:Subject {subject_key, study_key})``
* ``(:Visit   {visit_id, subject_key, study_key})``
* ``(:Record  {record_id, form_id, visit_id, subject_key, study_key, **record_data})``

Relationships
~~~~~~~~~~~~~
* ``(:Study)-[:HAS_SUBJECT]->(:Subject)``
* ``(:Subject)-[:HAS_VISIT]->(:Visit)``
* ``(:Visit)-[:HAS_RECORD]->(:Record)``

Optional dependency
-------------------
Requires ``neo4j`` (install via ``pip install 'imednet[neo4j]'``).
The driver is imported lazily at connection time so that importing this
module never fails when ``neo4j`` is not installed.

Idempotency
-----------
When ``SinkConfig.idempotent`` is ``True`` (default) the sink uses
``MERGE`` on the node's primary key property so that re-running an export
for the same batch updates existing nodes rather than creating duplicates.

Usage
-----
.. code-block:: python

    from imednet.integrations.graph import Neo4jExportSink, Neo4jSinkConfig
    from imednet_workflows.data_extraction import DataExtractionWorkflow

    records = DataExtractionWorkflow(sdk).extract_records_by_criteria(
        study_key="MYSTUDY",
    )

    config = Neo4jSinkConfig(batch_size=200)
    with Neo4jExportSink(
        uri="bolt://localhost:7687",
        auth=("neo4j", "password"),
        config=config,
    ) as sink:
        for i, batch in enumerate(batched(records, config.batch_size)):
            sink.write_batch(batch, batch_id=f"MYSTUDY/all/{i}")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional, Sequence, Tuple

from imednet.errors import ExportBatchError, ExportConfigurationError
from imednet.integrations.sink_base import (
    ExportSink,
    SinkConfig,
    _redact_uri,
    _require_optional_dep,
    iter_batches,
)
from imednet.sdk import ImednetSDK

logger = logging.getLogger(__name__)


@dataclass
class Neo4jSinkConfig(SinkConfig):
    """Extended :class:`~imednet.integrations.sink_base.SinkConfig` for Neo4j.

    Parameters
    ----------
    database:
        Target Neo4j database name (default ``"neo4j"``).
    """

    database: str = "neo4j"


# ---------------------------------------------------------------------------
# Cypher templates
# ---------------------------------------------------------------------------

_MERGE_RECORD_CYPHER = """\
UNWIND $rows AS row
MERGE (s:Study   {study_key:   row.study_key})
MERGE (su:Subject {subject_key: row.subject_key, study_key: row.study_key})
MERGE (v:Visit    {visit_id:   row.visit_id,    study_key: row.study_key})
MERGE (r:Record   {record_id:  row.record_id,   study_key: row.study_key})
SET r += row
MERGE (s)-[:HAS_SUBJECT]->(su)
MERGE (su)-[:HAS_VISIT]->(v)
MERGE (v)-[:HAS_RECORD]->(r)
"""

_CREATE_RECORD_CYPHER = """\
UNWIND $rows AS row
CREATE (r:Record)
SET r = row
WITH r, row
MATCH (v:Visit {visit_id: row.visit_id, study_key: row.study_key})
MERGE (v)-[:HAS_RECORD]->(r)
"""


def _record_to_row(record: Any, study_key: str) -> dict[str, Any]:
    """Convert a typed ``Record`` model to a flat Cypher parameter dict."""
    import json

    return {
        "record_id": getattr(record, "record_id", None),
        "form_id": getattr(record, "form_id", None),
        "form_key": getattr(record, "form_key", None),
        "visit_id": getattr(record, "visit_id", None),
        "subject_id": getattr(record, "subject_id", None),
        "subject_key": getattr(record, "subject_key", None),
        "study_key": study_key,
        "record_status": getattr(record, "record_status", None),
        "deleted": getattr(record, "deleted", None),
        "date_created": getattr(record, "date_created", None),
        "date_modified": getattr(record, "date_modified", None),
        "record_data": json.dumps(dict(getattr(record, "record_data", {}) or {})),
    }


class Neo4jExportSink(ExportSink):
    """Export iMednet records as Neo4j graph nodes and relationships.

    Parameters
    ----------
    uri:
        Neo4j Bolt or HTTP URI (e.g. ``"bolt://localhost:7687"`` or
        ``"neo4j+s://xxxx.databases.neo4j.io"``).
    auth:
        ``(username, password)`` tuple.  Credentials are never logged.
    study_key:
        Study identifier attached to every node for multi-study graphs.
    config:
        Optional :class:`Neo4jSinkConfig` (or plain :class:`SinkConfig`).
        Defaults to :class:`Neo4jSinkConfig` with all values at defaults.

    Raises:
    ------
    ~imednet.errors.ExportConfigurationError
        When the driver cannot connect to the database.
    ImportError
        When the ``neo4j`` package is not installed.
    """

    def __init__(
        self,
        uri: str,
        auth: Tuple[str, str],
        study_key: str,
        *,
        config: Optional[SinkConfig] = None,
    ) -> None:
        """Implementation detail."""
        super().__init__(config if config is not None else Neo4jSinkConfig())
        self._uri = uri
        self._auth = auth
        self._study_key = study_key
        self._driver: Any = None
        self._connect()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        """Perform  connect operation."""
        neo4j_mod = _require_optional_dep("neo4j", "neo4j")
        redacted = _redact_uri(self._uri)
        logger.debug("Connecting to Neo4j at %s", redacted)
        try:
            self._driver = neo4j_mod.GraphDatabase.driver(self._uri, auth=self._auth)
            self._driver.verify_connectivity()
        except Exception as exc:
            raise ExportConfigurationError(f"Cannot connect to Neo4j at {redacted}: {exc}") from exc

    # ------------------------------------------------------------------
    # ExportSink interface
    # ------------------------------------------------------------------

    def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:
        """Write *records* to Neo4j using MERGE (idempotent) or CREATE."""
        rows = [_record_to_row(r, self._study_key) for r in records]
        if not rows:
            return 0

        cypher = _MERGE_RECORD_CYPHER if self.config.idempotent else _CREATE_RECORD_CYPHER
        cfg = self.config if isinstance(self.config, Neo4jSinkConfig) else Neo4jSinkConfig()

        from imednet.core.operations.executor import UniversalExecutor

        def execute_export() -> int:
            """Perform execute export operation."""
            with self._driver.session(database=cfg.database) as session:
                session.run(cypher, rows=rows)
            logger.debug("Wrote batch %s (%d records)", batch_id, len(rows))
            return len(rows)

        executor = UniversalExecutor(
            retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            tracer=self.config.tracer,
            operation_name="export_graph",
            batch_id=batch_id,
        )

        try:
            return executor.execute(execute_export)
        except Exception as exc:
            raise ExportBatchError(
                f"Batch {batch_id!r} failed after {self.config.max_retries + 1} attempts: {exc}",
                batch_id=batch_id,
            ) from exc

    def flush(self) -> None:
        """No-op: Neo4j writes are committed per transaction."""

    def close(self) -> None:
        """Close the underlying Neo4j driver connection."""
        if self._driver is not None:
            try:
                self._driver.close()
            finally:
                self._driver = None


def export_to_neo4j(
    sdk: ImednetSDK,
    study_key: str,
    uri: str,
    auth: Tuple[str, str],
    *,
    config: Optional[Neo4jSinkConfig] = None,
) -> int:
    """Export study records to Neo4j using :class:`Neo4jExportSink`."""
    cfg = config if config is not None else Neo4jSinkConfig()
    records = sdk.records.list(study_key=study_key, record_data_filter=None)
    total_written = 0
    with Neo4jExportSink(uri, auth, study_key, config=cfg) as sink:
        for index, batch in enumerate(iter_batches(list(records), cfg.batch_size)):
            total_written += sink.write_batch(batch, batch_id=f"{study_key}/records/{index}")
    return total_written


__all__ = ["Neo4jExportSink", "Neo4jSinkConfig", "export_to_neo4j"]
