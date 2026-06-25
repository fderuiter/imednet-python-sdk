"""MongoDB document-envelope export sink.

This module implements the **structure-preserving export path** for a MongoDB
destination.  Records fetched via
:class:`~imednet_workflows.data_extraction.DataExtractionWorkflow` are wrapped
in a consistent document envelope that preserves the clinical hierarchy.

Document envelope
-----------------
Each document stored in MongoDB represents a single iMednet **Record** and
carries the metadata needed to locate and de-duplicate it:

.. code-block:: json

    {
        "_id": "<study_key>/<record_id>",
        "study_key":     "MYSTUDY",
        "record_id":     1234,
        "subject_id":    99,
        "subject_key":   "SUBJ-001",
        "visit_id":      42,
        "form_id":       7,
        "form_key":      "BASELINE",
        "record_status": "Complete",
        "deleted":       false,
        "date_created":  "2024-01-01T08:00:00Z",
        "date_modified": "2024-01-15T12:00:00Z",
        "record_data":   { "var1": "value1", "var2": 99 },
        "exported_at":   "2024-01-15T12:00:00Z"
    }

The ``_id`` field is a composite key ``<study_key>/<record_id>`` which
guarantees uniqueness within a collection and enables efficient upserts.

Optional dependency
-------------------
Requires ``pymongo`` (install via ``pip install 'imednet[mongodb]'``).
The client is imported lazily at connection time.

Idempotency
-----------
When ``SinkConfig.idempotent`` is ``True`` (default) the sink uses
``bulk_write`` with ``UpdateOne(..., upsert=True)`` operations so that
re-running an export for the same batch updates existing documents rather
than inserting duplicates.

Usage
-----
.. code-block:: python

    from imednet.integrations.document import MongoDbExportSink
    from imednet_workflows.data_extraction import DataExtractionWorkflow

    records = DataExtractionWorkflow(sdk).extract_records_by_criteria(
        study_key="MYSTUDY",
    )

    with MongoDbExportSink(
        uri="******localhost:27017",
        database="imednet",
        collection="records",
    ) as sink:
        for i, batch in enumerate(batched(records, 500)):
            sink.write_batch(batch, batch_id=f"MYSTUDY/all/{i}")
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional, Sequence

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


def _make_document_id(study_key: str, record_id: Any) -> str:
    """Return the composite ``_id`` for a MongoDB record document."""
    return f"{study_key}/{record_id}"


def _record_to_document(record: Any, study_key: str) -> dict[str, Any]:
    """Wrap a typed ``Record`` model in the standard document envelope."""
    record_id = getattr(record, "record_id", None)
    return {
        "_id": _make_document_id(study_key, record_id),
        "study_key": study_key,
        "record_id": record_id,
        "subject_id": getattr(record, "subject_id", None),
        "subject_key": getattr(record, "subject_key", None),
        "visit_id": getattr(record, "visit_id", None),
        "form_id": getattr(record, "form_id", None),
        "form_key": getattr(record, "form_key", None),
        "record_status": getattr(record, "record_status", None),
        "deleted": getattr(record, "deleted", None),
        "date_created": getattr(record, "date_created", None),
        "date_modified": getattr(record, "date_modified", None),
        "record_data": dict(getattr(record, "record_data", {}) or {}),
        "exported_at": datetime.now(tz=timezone.utc).isoformat(),
    }


class MongoDbExportSink(ExportSink):
    """Export iMednet records as MongoDB document envelopes.

    Parameters
    ----------
    uri:
        MongoDB connection URI
        (e.g. ``"******localhost:27017"``).
        Credentials are never logged.
    database:
        Target database name.
    collection:
        Target collection name.
    study_key:
        Study identifier embedded in every document and used to build the
        composite ``_id``.
    config:
        Optional :class:`~imednet.integrations.sink_base.SinkConfig`.

    Raises:
    ------
    ~imednet.errors.ExportConfigurationError
        When the client cannot connect to the server.
    ImportError
        When the ``pymongo`` package is not installed.
    """

    def __init__(
        self,
        uri: str,
        database: str,
        collection: str,
        study_key: str,
        *,
        config: Optional[SinkConfig] = None,
    ) -> None:
        """Implementation detail."""
        super().__init__(config)
        self._uri = uri
        self._database = database
        self._collection_name = collection
        self._study_key = study_key
        self._client: Any = None
        self._collection: Any = None
        self._connect()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        """Handle the connect process."""
        pymongo = _require_optional_dep("pymongo", "mongodb")
        redacted = _redact_uri(self._uri)
        logger.debug("Connecting to MongoDB at %s", redacted)
        try:
            self._client = pymongo.MongoClient(self._uri)
            # Force a connection check
            self._client.admin.command("ping")
            db = self._client[self._database]
            self._collection = db[self._collection_name]
        except Exception as exc:
            raise ExportConfigurationError(
                f"Cannot connect to MongoDB at {redacted}. Driver error type: {type(exc).__name__}"
            ) from exc

    # ------------------------------------------------------------------
    # ExportSink interface
    # ------------------------------------------------------------------

    def write_batch(self, records: Sequence[Any], *, batch_id: str) -> int:
        """Write *records* to MongoDB using upsert (idempotent) or insert."""
        docs = [_record_to_document(r, self._study_key) for r in records]
        if not docs:
            return 0

        from imednet.core.operations.executor import UniversalExecutor

        def execute_export() -> int:
            """Handle the execute export process."""
            if self.config.idempotent:
                pymongo = _require_optional_dep("pymongo", "mongodb")
                ops = [
                    pymongo.UpdateOne(
                        {"_id": doc["_id"]},
                        {"$set": doc},
                        upsert=True,
                    )
                    for doc in docs
                ]
                self._collection.bulk_write(ops, ordered=False)
                written = len(docs)
            else:
                result = self._collection.insert_many(docs, ordered=False)
                written = len(result.inserted_ids)

            logger.debug("Wrote batch %s (%d records)", batch_id, written)
            return written

        executor = UniversalExecutor(
            retries=self.config.max_retries,
            backoff_factor=self.config.retry_backoff,
            tracer=self.config.tracer,
            operation_name="export_mongodb",
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
        """No-op: MongoDB writes are committed per bulk operation."""

    def close(self) -> None:
        """Close the underlying PyMongo client."""
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None
                self._collection = None


def export_to_mongodb(
    sdk: ImednetSDK,
    study_key: str,
    uri: str,
    database: str,
    collection: str,
    *,
    config: Optional[SinkConfig] = None,
) -> int:
    """Export study records to MongoDB using :class:`MongoDbExportSink`."""
    from imednet.integrations.sink_base import apply_quality_gate

    cfg = config if config is not None else SinkConfig()
    records = sdk.records.list(study_key=study_key, record_data_filter=None)
    filtered_records = list(apply_quality_gate(sdk, study_key, records, cfg))

    total_written = 0
    with MongoDbExportSink(uri, database, collection, study_key, config=cfg) as sink:
        for index, batch in enumerate(iter_batches(filtered_records, cfg.batch_size)):
            total_written += sink.write_batch(batch, batch_id=f"{study_key}/records/{index}")
    return total_written


__all__ = ["MongoDbExportSink", "export_to_mongodb"]
