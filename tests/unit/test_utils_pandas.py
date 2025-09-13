import ast
from unittest.mock import MagicMock

import pandas as pd

from imednet.api.models.records import Record
from imednet.utils.pandas import export_records_csv, records_to_dataframe


def _sample_record() -> Record:
    return Record(
        record_id=1,
        subject_key="S1",
        visit_id=1,
        form_id=10,
        record_status="Complete",
        record_data={"AGE": 30},
    )


def test_records_to_dataframe_flatten() -> None:
    rec = _sample_record()
    df = records_to_dataframe([rec], flatten=True)
    assert "record_data" not in df.columns
    assert df.loc[0, "AGE"] == 30


def test_records_to_dataframe_no_flatten() -> None:
    rec = _sample_record()
    df = records_to_dataframe([rec], flatten=False)
    assert "record_data" in df.columns
    assert df.loc[0, "record_data"] == {"AGE": 30}


def test_records_to_dataframe_empty() -> None:
    df = records_to_dataframe([], flatten=False)
    assert df.empty


def test_export_records_csv(tmp_path) -> None:
    sdk = MagicMock()
    sdk.records.list.return_value = [_sample_record()]
    out_path = tmp_path / "records.csv"

    export_records_csv(sdk, "STUDY", str(out_path))

    assert out_path.exists()
    df = pd.read_csv(out_path)
    assert df.loc[0, "AGE"] == 30
    sdk.records.list.assert_called_once_with(study_key="STUDY")


def test_export_records_csv_no_flatten(tmp_path) -> None:
    sdk = MagicMock()
    sdk.records.list.return_value = [_sample_record()]
    out_path = tmp_path / "records.csv"

    export_records_csv(sdk, "STUDY", str(out_path), flatten=False)

    assert out_path.exists()
    df = pd.read_csv(out_path)
    assert "record_data" in df.columns
    assert ast.literal_eval(str(df.loc[0, "record_data"])) == {"AGE": 30}
    sdk.records.list.assert_called_once_with(study_key="STUDY")
