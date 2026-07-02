"""Unified functional facade for data export.

This module provides a single entry point `export()` for all data persistence tasks,
supporting both tabular procedural functions and object-oriented sink classes.
"""

from typing import Any, Callable, Dict, Optional, Type

from imednet.integrations.sink_base import ExportSink, SinkConfig, apply_quality_gate, iter_batches
from imednet.sdk import ImednetSDK


class ExportRegistry:
    """Central registry mapping target types to their implementations."""

    _LAZY_SINKS = {
        "mongodb": "imednet_sinks.document:MongoDbExportSink",
        "neo4j": "imednet_sinks.graph:Neo4jExportSink",
        "snowflake": "imednet_sinks.warehouse:SnowflakeExportSink",
    }

    def __init__(self):
        """Initialize an empty ExportRegistry."""
        self._tabular_targets: Dict[str, Callable] = {}
        self._sink_targets: Dict[str, Type[ExportSink]] = {}

    def register_tabular(self, target_type: str, func: Callable) -> None:
        """Register a tabular procedural function for a target type."""
        self._tabular_targets[target_type] = func

    def register_sink(self, target_type: str, sink_class: Type[ExportSink]) -> None:
        """Register an object-oriented sink class for a target type."""
        self._sink_targets[target_type] = sink_class

    def get_tabular(self, target_type: str) -> Optional[Callable]:
        """Retrieve a registered tabular function, or None if not found."""
        return self._tabular_targets.get(target_type)

    def get_sink(self, target_type: str) -> Optional[Type[ExportSink]]:
        """Retrieve a registered sink class, or None if not found."""
        if target_type in self._sink_targets:
            return self._sink_targets[target_type]

        # Lazy load known sinks
        if target_type in self._LAZY_SINKS:
            module_path, class_name = self._LAZY_SINKS[target_type].split(":")
            try:
                import importlib

                module = importlib.import_module(module_path)
                sink_class = getattr(module, class_name)
                self.register_sink(target_type, sink_class)
                return sink_class
            except (ImportError, AttributeError):
                return None

        return None


# Global registry instance
_registry = ExportRegistry()


def register_tabular_target(target_type: str, func: Callable) -> None:
    """Register a tabular procedural function for a target type."""
    _registry.register_tabular(target_type, func)


def register_sink_target(target_type: str, sink_class: Type[ExportSink]) -> None:
    """Register an object-oriented sink class for a target type."""
    _registry.register_sink(target_type, sink_class)


def export(
    target: str,
    sdk: ImednetSDK,
    study_key: str,
    *,
    config: Optional[SinkConfig] = None,
    **kwargs: Any,
) -> Any:
    """Unified entry point for data export.

    Routes the export request to either a tabular function or a sink class
    based on the target identifier.

    Args:
        target: The target destination type (e.g., 'csv', 'snowflake', 'mongodb').
        sdk: Authenticated SDK instance used to fetch study records.
        study_key: Study identifier to export.
        config: Optional sink configuration (for sink-based targets).
        **kwargs: Target-specific configuration parameters.

    Returns:
        For tabular targets: Typically None.
        For sink targets: The total number of records successfully written.

    Raises:
        ValueError: If the target type is not registered or unsupported.
    """
    # 1. Try tabular path
    tabular_func = _registry.get_tabular(target)
    if tabular_func is not None:
        return tabular_func(sdk, study_key, **kwargs)

    # 2. Try sink path
    sink_class = _registry.get_sink(target)
    if sink_class is not None:
        cfg = config if config is not None else SinkConfig()

        records = sdk.records.list(study_key=study_key, record_data_filter=None)
        filtered_records = list(apply_quality_gate(sdk, study_key, records, cfg))

        total_written = 0

        # Instantiate sink class using kwargs and cfg
        # We assume sink constructors accept config=cfg and **kwargs
        with sink_class(config=cfg, **kwargs) as sink:
            for index, batch in enumerate(iter_batches(filtered_records, cfg.batch_size)):
                total_written += sink.write_batch(batch, batch_id=f"{study_key}/records/{index}")

        return total_written

    raise ValueError(f"Unsupported export target: {target!r}")
