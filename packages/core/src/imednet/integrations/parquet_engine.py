"""Partitioned Parquet storage engines."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


def _import_pyarrow() -> tuple[Any, Any]:
    try:
        pyarrow_module = import_module("pyarrow")
        dataset_module = import_module("pyarrow.dataset")
    except ImportError as error:
        raise ImportError(
            "PyArrow is required for partitioned Parquet storage. "
            "Install with \"pip install 'imednet[export]'\"."
        ) from error
    return pyarrow_module, dataset_module


@runtime_checkable
class PartitionedStorageEngine(Protocol):
    """Interface for writing tables into a partitioned dataset."""

    def write_form_table(
        self,
        table: Any,
        *,
        base_dir: str,
        study_key: str,
        form_key: str,
    ) -> None:
        """Persist a form table into a partitioned dataset layout."""


@dataclass(frozen=True)
class PyArrowDatasetPartitionedStorageEngine:
    """Partitioned storage engine powered by ``pyarrow.dataset.write_dataset``."""

    compression: str = "snappy"
    use_dictionary: bool = True
    existing_data_behavior: str = "overwrite_or_ignore"

    def write_form_table(
        self,
        table: Any,
        *,
        base_dir: str,
        study_key: str,
        form_key: str,
    ) -> None:
        pyarrow_module, dataset_module = _import_pyarrow()
        partition_schema = pyarrow_module.schema(
            [
                ("study_key", pyarrow_module.string()),
                ("form_key", pyarrow_module.string()),
            ]
        )
        partitioned_table = table.append_column(
            "study_key",
            pyarrow_module.array([study_key] * table.num_rows, type=pyarrow_module.string()),
        ).append_column(
            "form_key",
            pyarrow_module.array([form_key] * table.num_rows, type=pyarrow_module.string()),
        )
        parquet_format = dataset_module.ParquetFileFormat()
        parquet_options = parquet_format.make_write_options(
            compression=self.compression,
            use_dictionary=self.use_dictionary,
        )
        dataset_module.write_dataset(
            partitioned_table,
            base_dir=str(Path(base_dir)),
            partitioning=dataset_module.partitioning(flavor="hive", schema=partition_schema),
            format=parquet_format,
            file_options=parquet_options,
            existing_data_behavior=self.existing_data_behavior,
        )


__all__ = ["PartitionedStorageEngine", "PyArrowDatasetPartitionedStorageEngine"]
