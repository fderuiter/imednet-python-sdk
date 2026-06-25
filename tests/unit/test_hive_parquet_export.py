"""Unit tests for hive parquet export."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

import imednet.integrations.parquet as parquet_mod


def _read_partition_dataframe(path: Path) -> pd.DataFrame:
    """Helper function to  read partition dataframe."""
    parquet_files = sorted(path.glob("**/*.parquet"))
    assert parquet_files
    return pd.read_parquet(parquet_files[0], engine="pyarrow")


def test_export_to_hive_parquet_directory_structure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that export to hive parquet directory structure."""
    pytest.importorskip("pyarrow")

    sdk = MagicMock()
    sdk.forms.list.return_value = [SimpleNamespace(form_id=1, form_key="DEMOGRAPHICS")]
    sdk.variables.list.return_value = [SimpleNamespace(form_id=1, variable_name="age", label="Age")]

    class FakeMapper:
        """Test suite for FakeMapper."""

        def __init__(self, sdk: MagicMock) -> None:
            """Initialize the test object."""
            self._sdk = sdk

        def _build_record_model(
            self, variable_keys: list[str], label_map: dict[str, str]
        ) -> tuple[list[str], dict[str, str]]:
            """Helper function to  build record model."""
            return (variable_keys, label_map)

        def _fetch_records(self, _study_key: str, extra_filters: dict[str, Any]) -> list[int]:
            """Helper function to  fetch records."""
            return [extra_filters["formId"]]

        def _parse_records(
            self,
            records: list[int],
            _record_model: tuple[list[str], dict[str, str]],
        ) -> tuple[list[int], int]:
            """Helper function to  parse records."""
            return records, len(records)

        def _build_dataframe(
            self,
            rows: list[int],
            _variable_keys: list[str],
            _label_map: dict[str, str],
            _use_labels_as_columns: bool,
        ) -> pd.DataFrame:
            """Helper function to  build dataframe."""
            return pd.DataFrame([{"age": rows[0]}])

    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: FakeMapper)

    parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", str(tmp_path))

    assert (tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS").exists()


def test_export_to_hive_parquet_concurrent_studies_no_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that export to hive parquet concurrent studies no conflict."""
    pytest.importorskip("pyarrow")

    sdk = MagicMock()
    sdk.forms.list.return_value = [SimpleNamespace(form_id=1, form_key="DEMOGRAPHICS")]
    sdk.variables.list.return_value = [
        SimpleNamespace(form_id=1, variable_name="study", label="Study")
    ]

    class FakeMapper:
        """Test suite for FakeMapper."""

        def __init__(self, sdk: MagicMock) -> None:
            """Initialize the test object."""
            self._sdk = sdk

        def _build_record_model(
            self, variable_keys: list[str], label_map: dict[str, str]
        ) -> tuple[list[str], dict[str, str]]:
            """Helper function to  build record model."""
            return (variable_keys, label_map)

        def _fetch_records(
            self, study_key: str, extra_filters: dict[str, Any] | None = None
        ) -> list[str]:
            """Helper function to  fetch records."""
            assert extra_filters is not None
            assert "formId" in extra_filters
            return [study_key]

        def _parse_records(
            self,
            records: list[str],
            _record_model: tuple[list[str], dict[str, str]],
        ) -> tuple[list[str], int]:
            """Helper function to  parse records."""
            return records, len(records)

        def _build_dataframe(
            self,
            rows: list[str],
            _variable_keys: list[str],
            _label_map: dict[str, str],
            _use_labels_as_columns: bool,
        ) -> pd.DataFrame:
            """Helper function to  build dataframe."""
            return pd.DataFrame([{"study": rows[0]}])

    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: FakeMapper)

    parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", str(tmp_path))
    parquet_mod.export_to_hive_parquet(sdk, "STUDY_B", str(tmp_path))

    study_a = _read_partition_dataframe(tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS")
    study_b = _read_partition_dataframe(tmp_path / "study_key=STUDY_B" / "form_key=DEMOGRAPHICS")

    assert study_a.to_dict("records") == [{"study": "STUDY_A"}]
    assert study_b.to_dict("records") == [{"study": "STUDY_B"}]


def test_hive_parquet_query_returns_correct_string() -> None:
    """Test that hive parquet query returns correct string."""
    assert (
        parquet_mod.hive_parquet_query("/tmp/lake")
        == "SELECT * FROM read_parquet('/tmp/lake/**/*.parquet', "
        "hive_partitioning = true, union_by_name = true)"
    )


def test_export_to_hive_parquet_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that export to hive parquet import error."""

    def _raise_import_error(module_name: str):
        """Helper function to  raise import error."""
        if module_name == "pyarrow":
            raise ImportError("missing pyarrow")
        return __import__(module_name)

    monkeypatch.setattr(parquet_mod, "import_module", _raise_import_error)

    with pytest.raises(ImportError, match=r"pip install"):
        parquet_mod.export_to_hive_parquet(MagicMock(), "STUDY", "/tmp/lake")
