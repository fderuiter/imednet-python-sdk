from typing import Any

import pytest

from imednet.integrations.parquet_engine import PyArrowDatasetPartitionedStorageEngine


class _FakeTable:
    def __init__(self) -> None:
        self.num_rows = 2
        self.columns: list[tuple[str, list[str]]] = []

    def append_column(self, name: str, values: list[str]) -> "_FakeTable":
        self.columns.append((name, values))
        return self


class _FakeParquetFormat:
    def __init__(self) -> None:
        self.options: dict[str, Any] | None = None

    def make_write_options(self, **kwargs: Any) -> dict[str, Any]:
        self.options = kwargs
        return kwargs


class _FakeDatasetModule:
    def __init__(self) -> None:
        self.partitioning_args: dict[str, Any] | None = None
        self.write_call: dict[str, Any] | None = None
        self.format = _FakeParquetFormat()

    def ParquetFileFormat(self) -> _FakeParquetFormat:  # noqa: N802
        return self.format

    def partitioning(self, **kwargs: Any) -> dict[str, Any]:
        self.partitioning_args = kwargs
        return kwargs

    def write_dataset(self, table: _FakeTable, **kwargs: Any) -> None:
        self.write_call = {"table": table, **kwargs}


class _FakePyArrowModule:
    def string(self) -> str:
        return "string"

    def schema(self, fields: list[tuple[str, str]]) -> list[tuple[str, str]]:
        return fields

    def array(self, values: list[str], **kwargs: Any) -> list[str]:
        assert kwargs["type"] == "string"
        return values


def test_pyarrow_dataset_partitioned_storage_engine_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_pa = _FakePyArrowModule()
    fake_ds = _FakeDatasetModule()
    monkeypatch.setattr(
        "imednet.integrations.parquet_engine._import_pyarrow",
        lambda: (fake_pa, fake_ds),
    )

    table = _FakeTable()
    engine = PyArrowDatasetPartitionedStorageEngine()
    engine.write_form_table(
        table,
        base_dir="/tmp/lake",
        study_key="STUDY_A",
        form_key="DEMOGRAPHICS",
    )

    assert fake_ds.format.options == {"compression": "snappy", "use_dictionary": True}
    assert fake_ds.partitioning_args == {
        "flavor": "hive",
        "schema": [("study_key", "string"), ("form_key", "string")],
    }
    assert fake_ds.write_call is not None
    assert fake_ds.write_call["base_dir"] == "/tmp/lake"
    assert fake_ds.write_call["existing_data_behavior"] == "overwrite_or_ignore"
    assert table.columns == [
        ("study_key", ["STUDY_A", "STUDY_A"]),
        ("form_key", ["DEMOGRAPHICS", "DEMOGRAPHICS"]),
    ]
