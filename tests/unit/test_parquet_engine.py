"""Test Parquet Engine module."""

from pathlib import Path
from typing import Any

import pytest

from imednet.integrations.parquet_engine import PyArrowDatasetPartitionedStorageEngine


class _FakeTable:
    """Test suite for _FakeTable."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        self.num_rows = 2
        self.columns: list[tuple[str, list[str]]] = []

    def append_column(self, name: str, values: list[str]) -> "_FakeTable":
        """Test the append column functionality."""
        self.columns.append((name, values))
        return self

    def value_for_column(self, name: str) -> Any:
        """Test the value for column functionality."""
        for column_name, values in self.columns:
            if column_name == name:
                return values[0]
        raise AssertionError(f"Missing expected column {name!r}")


class _FakeParquetFormat:
    """Test suite for _FakeParquetFormat."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        self.options: dict[str, Any] | None = None

    def make_write_options(self, **kwargs: Any) -> dict[str, Any]:
        """Test the make write options functionality."""
        self.options = kwargs
        return kwargs


class _FakeDatasetModule:
    """Test suite for _FakeDatasetModule."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        self.partitioning_args: dict[str, Any] | None = None
        self.write_call: dict[str, Any] | None = None
        self.format = _FakeParquetFormat()
        self.should_fail = False

    def ParquetFileFormat(self) -> _FakeParquetFormat:  # noqa: N802
        """Test the ParquetFileFormat functionality."""
        return self.format

    def partitioning(self, **kwargs: Any) -> dict[str, Any]:
        """Test the partitioning functionality."""
        self.partitioning_args = kwargs
        return kwargs

    def write_dataset(self, table: _FakeTable, **kwargs: Any) -> None:
        """Test the write dataset functionality."""
        if self.should_fail:
            raise RuntimeError("boom")
        base_dir = Path(kwargs["base_dir"])
        study_key = table.value_for_column("study_key")
        form_key = table.value_for_column("form_key")
        partition_dir = base_dir / f"study_key={study_key}" / f"form_key={form_key}"
        partition_dir.mkdir(parents=True, exist_ok=True)
        (partition_dir / "part-0.parquet").write_bytes(b"parquet")
        self.write_call = {"table": table, **kwargs}


class _FakePyArrowModule:
    """Test suite for _FakePyArrowModule."""

    def string(self) -> str:
        """Test the string functionality."""
        return "string"

    def schema(self, fields: list[tuple[str, str]]) -> list[tuple[str, str]]:
        """Test the schema functionality."""
        return fields

    def array(self, values: list[str], **kwargs: Any) -> list[str]:
        """Test the array functionality."""
        assert kwargs["type"] == "string"
        return values


def _raise_replace_failure(*_args: Any) -> None:
    """Test the raise replace failure functionality."""
    raise OSError("rename failed")


def test_pyarrow_dataset_partitioned_storage_engine_defaults(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test pyarrow dataset partitioned storage engine defaults functionality."""
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
        base_dir=str(tmp_path),
        study_key="STUDY_A",
        form_key="DEMOGRAPHICS",
    )

    assert fake_ds.format.options == {"compression": "snappy", "use_dictionary": True}
    assert fake_ds.partitioning_args == {
        "flavor": "hive",
        "schema": [("study_key", "string"), ("form_key", "string")],
    }
    assert fake_ds.write_call is not None
    assert "/.imednet_staging/" in fake_ds.write_call["base_dir"]
    assert fake_ds.write_call["existing_data_behavior"] == "overwrite_or_ignore"
    assert table.columns == [
        ("study_key", ["STUDY_A", "STUDY_A"]),
        ("form_key", ["DEMOGRAPHICS", "DEMOGRAPHICS"]),
    ]
    files = list((tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS").glob("**/*.parquet"))
    assert len(files) >= 1


def test_pyarrow_dataset_partitioned_storage_engine_cleans_staging_on_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test pyarrow dataset partitioned storage engine cleans staging on failure functionality."""
    fake_pa = _FakePyArrowModule()
    fake_ds = _FakeDatasetModule()
    fake_ds.should_fail = True
    monkeypatch.setattr(
        "imednet.integrations.parquet_engine._import_pyarrow",
        lambda: (fake_pa, fake_ds),
    )

    with pytest.raises(RuntimeError, match="boom"):
        PyArrowDatasetPartitionedStorageEngine().write_form_table(
            _FakeTable(),
            base_dir=str(tmp_path),
            study_key="STUDY_A",
            form_key="DEMOGRAPHICS",
        )

    assert not (tmp_path / ".imednet_staging").exists()
    assert not (tmp_path / "study_key=STUDY_A").exists()


def test_pyarrow_dataset_partitioned_storage_engine_cleans_visible_dirs_on_commit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the test pyarrow dataset partitioned storage engine cleans visible dirs on commit failure functionality."""
    fake_pa = _FakePyArrowModule()
    fake_ds = _FakeDatasetModule()
    monkeypatch.setattr(
        "imednet.integrations.parquet_engine._import_pyarrow",
        lambda: (fake_pa, fake_ds),
    )
    monkeypatch.setattr(
        "imednet.integrations.parquet_engine.os.replace",
        _raise_replace_failure,
    )

    with pytest.raises(OSError, match="rename failed"):
        PyArrowDatasetPartitionedStorageEngine().write_form_table(
            _FakeTable(),
            base_dir=str(tmp_path),
            study_key="STUDY_A",
            form_key="DEMOGRAPHICS",
        )

    assert not (tmp_path / ".imednet_staging").exists()
    assert not (tmp_path / "study_key=STUDY_A").exists()


def test_pyarrow_dataset_partitioned_storage_engine_schema_drift_duckdb(
    tmp_path: Path,
) -> None:
    """Test the test pyarrow dataset partitioned storage engine schema drift duckdb functionality."""
    duckdb = pytest.importorskip("duckdb")
    pyarrow = pytest.importorskip("pyarrow")
    parquet_module = pytest.importorskip("pyarrow.parquet")

    engine = PyArrowDatasetPartitionedStorageEngine()
    table_v1 = pyarrow.table({"id": [1], "age": [42]})
    table_v2 = pyarrow.table({"id": [2], "weight": [73.5]})

    engine.write_form_table(
        table_v1,
        base_dir=str(tmp_path),
        study_key="STUDY_A",
        form_key="DEMOGRAPHICS",
    )
    engine.write_form_table(
        table_v2,
        base_dir=str(tmp_path),
        study_key="STUDY_A",
        form_key="DEMOGRAPHICS",
    )

    files = sorted((tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS").glob("**/*.parquet"))
    assert len(files) == 2

    metadata = parquet_module.read_metadata(str(files[0])).metadata
    assert metadata is not None
    assert metadata[b"imednet.writer"] == b"pyarrow.dataset"
    assert b"imednet.commit_id" in metadata

    rows = (
        duckdb.connect(":memory:")
        .execute(
            "SELECT id, age, weight, study_key, form_key "
            "FROM read_parquet(?, hive_partitioning=true, union_by_name=true) "
            "ORDER BY id",
            [str(tmp_path / "**/*.parquet")],
        )
        .fetchall()
    )
    assert rows == [
        (1, 42, None, "STUDY_A", "DEMOGRAPHICS"),
        (2, None, 73.5, "STUDY_A", "DEMOGRAPHICS"),
    ]
