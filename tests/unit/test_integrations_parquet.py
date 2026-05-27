from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pandas as pd
import pytest

import imednet.integrations.parquet as parquet_mod
from imednet.errors import PathTraversalValidationError


def _read_partition_dataframe(path: Path) -> pd.DataFrame:
    parquet_files = sorted(path.glob("**/*.parquet"))
    assert parquet_files
    return pd.read_parquet(parquet_files[0], engine="pyarrow")


def test_export_creates_hive_layout_and_contents(tmp_path, monkeypatch) -> None:
    pytest.importorskip("pyarrow")

    sdk = MagicMock()
    sdk.forms.list.return_value = [
        SimpleNamespace(form_id=1, form_key="DEMOGRAPHICS"),
        SimpleNamespace(form_id=2, form_key="VITALS"),
    ]
    sdk.variables.list.return_value = [
        SimpleNamespace(form_id=1, variable_name="age", label="Age"),
        SimpleNamespace(form_id=2, variable_name="weight", label="Weight"),
    ]

    class FakeMapper:
        def __init__(self, _sdk) -> None:
            self._sdk = _sdk

        def _build_record_model(self, variable_keys, label_map):
            return (variable_keys, label_map)

        def _fetch_records(self, _study_key, extra_filters):
            return [extra_filters["formId"]]

        def _parse_records(self, records, _record_model):
            return records, len(records)

        def _build_dataframe(self, rows, _variable_keys, _label_map, _use_labels_as_columns):
            form_id = rows[0]
            if form_id == 1:
                return pd.DataFrame([{"age": 42}])
            return pd.DataFrame([{"weight": 73.5}])

    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: FakeMapper)

    parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", str(tmp_path))

    demographics_path = tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS"
    vitals_path = tmp_path / "study_key=STUDY_A" / "form_key=VITALS"
    assert demographics_path.exists()
    assert vitals_path.exists()

    demographics_df = _read_partition_dataframe(demographics_path)
    vitals_df = _read_partition_dataframe(vitals_path)
    assert demographics_df.to_dict("records") == [{"age": 42}]
    assert vitals_df.to_dict("records") == [{"weight": 73.5}]


def test_export_isolates_studies(tmp_path, monkeypatch) -> None:
    pytest.importorskip("pyarrow")

    sdk = MagicMock()
    sdk.forms.list.return_value = [SimpleNamespace(form_id=1, form_key="DEMOGRAPHICS")]
    sdk.variables.list.return_value = [SimpleNamespace(form_id=1, variable_name="age", label="Age")]

    class FakeMapper:
        def __init__(self, _sdk) -> None:
            self._sdk = _sdk

        def _build_record_model(self, variable_keys, label_map):
            return (variable_keys, label_map)

        def _fetch_records(self, study_key, extra_filters):
            return [(study_key, extra_filters["formId"])]

        def _parse_records(self, records, _record_model):
            return records, len(records)

        def _build_dataframe(self, rows, _variable_keys, _label_map, _use_labels_as_columns):
            study_key, _form_id = rows[0]
            return pd.DataFrame([{"study": study_key}])

    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: FakeMapper)

    parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", str(tmp_path))
    parquet_mod.export_to_hive_parquet(sdk, "STUDY_B", str(tmp_path))

    study_a_path = tmp_path / "study_key=STUDY_A" / "form_key=DEMOGRAPHICS"
    study_b_path = tmp_path / "study_key=STUDY_B" / "form_key=DEMOGRAPHICS"
    assert study_a_path.exists()
    assert study_b_path.exists()

    assert _read_partition_dataframe(study_a_path).to_dict("records") == [{"study": "STUDY_A"}]
    assert _read_partition_dataframe(study_b_path).to_dict("records") == [{"study": "STUDY_B"}]


def test_hive_parquet_query() -> None:
    assert (
        parquet_mod.hive_parquet_query("/tmp/lake")
        == "SELECT * FROM read_parquet('/tmp/lake/**/*.parquet', hive_partitioning = true)"
    )


def test_export_to_hive_parquet_missing_pyarrow(monkeypatch) -> None:
    def _raise_import_error(module_name: str):
        if module_name == "pyarrow":
            raise ImportError("missing pyarrow")
        return __import__(module_name)

    monkeypatch.setattr(parquet_mod, "import_module", _raise_import_error)

    with pytest.raises(ImportError, match=r"pip install 'imednet\[export\]'"):
        parquet_mod.export_to_hive_parquet(MagicMock(), "STUDY_A", "/tmp/lake")


def test_export_to_hive_parquet_rejects_malicious_study_key(monkeypatch) -> None:
    monkeypatch.setattr(parquet_mod, "_ensure_pyarrow", lambda: None)

    sdk = MagicMock()

    with pytest.raises(PathTraversalValidationError):
        parquet_mod.export_to_hive_parquet(sdk, "../STUDY_A", "/tmp/lake")

    sdk.forms.list.assert_not_called()


def test_export_to_hive_parquet_rejects_malicious_form_key(monkeypatch) -> None:
    monkeypatch.setattr(parquet_mod, "_ensure_pyarrow", lambda: None)

    sdk = MagicMock()
    sdk.forms.list.return_value = [SimpleNamespace(form_id=1, form_key="../DEMOGRAPHICS")]
    sdk.variables.list.return_value = []
    mapper_factory = MagicMock()
    mapper = mapper_factory.return_value
    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: mapper_factory)

    with pytest.raises(PathTraversalValidationError):
        parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", "/tmp/lake")

    mapper._fetch_records.assert_not_called()


def test_export_to_hive_parquet_flushes_form_batches(monkeypatch, tmp_path) -> None:
    sdk = MagicMock()
    sdk.forms.list.return_value = [SimpleNamespace(form_id=1, form_key="DEMOGRAPHICS")]
    sdk.variables.list.return_value = [SimpleNamespace(form_id=1, variable_name="age", label="Age")]

    class FakeMapper:
        def __init__(self, _sdk) -> None:
            self._sdk = _sdk

        def _build_record_model(self, variable_keys, label_map):
            return (variable_keys, label_map)

        def _iter_records(self, _study_key, extra_filters):
            assert extra_filters == {"formIds": [1]}
            return iter([1, 2, 3])

        def _iter_parsed_rows(self, records, _record_model):
            values = list(records)
            yield values[:2], 0
            yield values[2:], 0

        def _build_dataframe(self, rows, _variable_keys, _label_map, _use_labels_as_columns):
            return pd.DataFrame([{"age": value} for value in rows])

    writes: list[list[dict[str, int]]] = []

    class FakeEngine:
        def write_form_table(self, table, **kwargs) -> None:
            assert kwargs == {
                "base_dir": str(tmp_path),
                "study_key": "STUDY_A",
                "form_key": "DEMOGRAPHICS",
            }
            writes.append(table.to_dict("records"))

    class _FakeTable:
        @staticmethod
        def from_pandas(df: pd.DataFrame, preserve_index: bool = False) -> pd.DataFrame:
            assert preserve_index is False
            return df

    monkeypatch.setattr(parquet_mod, "_record_mapper", lambda: FakeMapper)
    monkeypatch.setattr(parquet_mod, "_ensure_pyarrow", lambda: SimpleNamespace(Table=_FakeTable))
    monkeypatch.setattr(parquet_mod, "PyArrowDatasetPartitionedStorageEngine", lambda: FakeEngine())

    parquet_mod.export_to_hive_parquet(sdk, "STUDY_A", str(tmp_path), chunk_size=2)

    assert writes == [[{"age": 1}, {"age": 2}], [{"age": 3}]]
