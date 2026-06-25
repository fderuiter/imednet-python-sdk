"""Unit tests for utils pandas."""

import ast
from unittest.mock import MagicMock

import pandas as pd
import pytest

from imednet.models.records import Record
from imednet.utils.pandas import export_records_csv, records_to_dataframe


def _sample_record() -> Record:
    """Helper function to  sample record."""
    return Record(
        record_id=1,
        subject_key="S1",
        visit_id=1,
        form_id=10,
        record_status="Complete",
        record_data={"AGE": 30},
    )


def test_records_to_dataframe_flatten() -> None:
    """Test that records to dataframe flatten."""
    rec = _sample_record()
    df = records_to_dataframe([rec], flatten=True)
    assert "record_data" not in df.columns
    assert df.loc[0, "AGE"] == 30


def test_records_to_dataframe_no_flatten() -> None:
    """Test that records to dataframe no flatten."""
    rec = _sample_record()
    df = records_to_dataframe([rec], flatten=False)
    assert "record_data" in df.columns
    assert df.loc[0, "record_data"] == {"AGE": 30}


def test_records_to_dataframe_empty() -> None:
    """Test that records to dataframe empty."""
    df = records_to_dataframe([], flatten=False)
    assert df.empty


def test_export_records_csv(tmp_path) -> None:
    """Test that export records csv."""
    sdk = MagicMock()
    sdk.records.list.return_value = [_sample_record()]
    out_path = tmp_path / "records.csv"

    export_records_csv(sdk, "STUDY", str(out_path))

    assert out_path.exists()
    df = pd.read_csv(out_path)
    assert df.loc[0, "AGE"] == 30
    sdk.records.list.assert_called_once_with(study_key="STUDY")


def test_export_records_csv_no_flatten(tmp_path) -> None:
    """Test that export records csv no flatten."""
    sdk = MagicMock()
    sdk.records.list.return_value = [_sample_record()]
    out_path = tmp_path / "records.csv"

    export_records_csv(sdk, "STUDY", str(out_path), flatten=False)

    assert out_path.exists()
    df = pd.read_csv(out_path)
    assert "record_data" in df.columns
    assert ast.literal_eval(str(df.loc[0, "record_data"])) == {"AGE": 30}
    sdk.records.list.assert_called_once_with(study_key="STUDY")


def test_records_to_dataframe_raises_importerror_when_pandas_missing(monkeypatch):
    """Test that records to dataframe raises importerror when pandas missing."""
    monkeypatch.setattr("imednet.utils.pandas.pd", None)
    with pytest.raises(ImportError, match="pandas is required for records_to_dataframe"):
        records_to_dataframe([])


def test_export_records_csv_raises_importerror_when_pandas_missing(monkeypatch):
    """Test that export records csv raises importerror when pandas missing."""
    monkeypatch.setattr("imednet.utils.pandas.pd", None)
    with pytest.raises(ImportError, match="pandas is required for export_records_csv"):
        export_records_csv(None, "STUDY", "path.csv")
