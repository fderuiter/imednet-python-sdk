"""Airflow operator for exporting study records."""

from __future__ import annotations

import logging
import time
from collections.abc import Mapping, Sequence
from typing import Any

from imednet import ImednetSDK
from imednet.spi import sink_base

SinkConfig = sink_base.SinkConfig
apply_quality_gate = sink_base.apply_quality_gate
iter_batches = sink_base.iter_batches

from .. import export
from .._airflow_compat import AirflowException, Context
from ..hooks import ImednetHook

try:  # pragma: no cover - optional Airflow dependency
    from airflow.models import BaseOperator  # type: ignore
except (ImportError, ModuleNotFoundError):  # pragma: no cover - placeholder fallback

    class BaseOperator:  # type: ignore
        """TODO: Add docstring."""

        template_fields: Sequence[str] = ()

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """TODO: Add docstring."""
            pass


logger = logging.getLogger(__name__)

# Fallback mapping for tabular exports if the user explicitly needs them or backward compatibility
_TABULAR_EXPORTS = {
    "csv": export.export_to_csv,
    "parquet": export.export_to_parquet,
    "excel": export.export_to_excel,
    "json": export.export_to_json,
    "sql": export.export_to_sql,
    "duckdb": getattr(export, "export_to_duckdb", None),
}


class ImednetExportOperator(BaseOperator):
    """Unified Airflow operator for exporting study records to any destination."""

    # Fields intended for Airflow `.partial().expand()` runtime mapping.
    mapped_runtime_fields: Sequence[str] = ("study_key", "output_path", "export_kwargs")
    template_fields: Sequence[str] = mapped_runtime_fields
    template_fields_renderers = {"export_kwargs": "json"}

    def __init__(
        self,
        *,
        study_key: str,
        destination: str | None = None,
        output_path: str | None = None,
        export_func: str | None = None,
        export_kwargs: Mapping[str, Any] | None = None,
        imednet_conn_id: str = "imednet_default",
        batch_size: int = 500,
        max_retries: int = 3,
        idempotent: bool = True,
        **kwargs: Any,
    ) -> None:
        """TODO: Add docstring."""
        super().__init__(**kwargs)
        self.study_key = study_key
        self.destination = destination
        self.output_path = output_path
        self.export_func = export_func
        self.export_kwargs = dict(export_kwargs or {})
        self.imednet_conn_id = imednet_conn_id

        # Common operational parameters
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.idempotent = idempotent

    def _get_sdk(self) -> ImednetSDK:
        """Resolve the SDK client from the configured Airflow connection at execute time."""
        return ImednetHook(self.imednet_conn_id).get_sdk_client()

    def _get_runtime_export_kwargs(self) -> dict[str, Any]:
        """Return a defensive copy of export kwargs for mapped task isolation."""
        return dict(self.export_kwargs)

    def _resolve_sink(self, config: SinkConfig) -> Any:
        """Dynamically load and configure the target sink, handling dependencies lazily."""
        dest = self.destination
        if not dest and self.export_func:
            dest = self.export_func.replace("export_to_", "")

        if dest == "snowflake":
            from imednet_sinks import SnowflakeExportSink  # type: ignore

            return SnowflakeExportSink(config=config)
        elif dest == "neo4j":
            from imednet_sinks import Neo4jExportSink  # type: ignore

            return Neo4jExportSink(
                uri=self.export_kwargs.get("uri", ""),
                auth=self.export_kwargs.get("auth", ("", "")),
                study_key=self.study_key,
                config=config,  # type: ignore
            )
        elif dest == "mongodb":
            from imednet_sinks import MongoDbExportSink  # type: ignore

            return MongoDbExportSink(
                uri=self.export_kwargs.get("uri", ""),
                database=self.export_kwargs.get("database", ""),
                collection=self.export_kwargs.get("collection", ""),
                study_key=self.study_key,
                config=config,  # type: ignore
            )
        return None

    def execute(self, context: Context) -> str | None:
        """TODO: Add docstring."""
        # Resolve destination early to fail fast on invalid configs (like legacy _get_export_callable)
        dest = self.destination
        if not dest and self.export_func:
            dest = self.export_func.replace("export_to_", "")
        elif not dest:
            dest = "csv"

        export_callable = None
        if dest in _TABULAR_EXPORTS:
            export_callable = getattr(export, f"export_to_{dest}", _TABULAR_EXPORTS[dest])
        elif self.export_func and hasattr(export, self.export_func):
            export_callable = getattr(export, self.export_func)

        sink = None
        if not export_callable:
            config_for_check = SinkConfig()
            sink = self._resolve_sink(config_for_check)
            if not sink:
                raise AirflowException(
                    f"Unsupported export_func '{self.export_func or dest}'. Expected a valid destination or tabular function."
                )

        sdk = self._get_sdk()

        config = SinkConfig(
            batch_size=self.batch_size,
            max_retries=self.max_retries,
            idempotent=self.idempotent,
            extra=self._get_runtime_export_kwargs(),
        )

        sink = self._resolve_sink(config)

        attempts = 0
        while attempts <= config.max_retries:
            try:
                if sink:
                    # Single execution path for Sink-based destinations
                    raw_records = sdk.records.list(
                        study_key=self.study_key, record_data_filter=None
                    )
                    records_list = list(
                        apply_quality_gate(sdk, self.study_key, raw_records, config)
                    )
                    with sink:
                        for i, batch in enumerate(iter_batches(records_list, config.batch_size)):
                            sink.write_batch(batch, batch_id=f"{self.study_key}/batch/{i}")
                else:
                    # Execution path for legacy tabular functions
                    # We dispatch to getattr so mocks in tests are preserved
                    if not export_callable:
                        raise AirflowException(f"Unsupported destination or export_func '{dest}'")

                    export_callable(
                        sdk, self.study_key, self.output_path, **self._get_runtime_export_kwargs()
                    )
                return self.output_path
            except Exception as e:
                attempts += 1
                if attempts > config.max_retries:
                    raise
                logger.warning("Export attempt %d failed: %s. Retrying...", attempts, e)
                time.sleep(config.retry_backoff * (2 ** (attempts - 1)))

        return self.output_path


__all__ = ["ImednetExportOperator"]
