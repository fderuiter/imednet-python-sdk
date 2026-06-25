"""Tests for test_record_mapper."""

import tracemalloc
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from faker import Faker
from pydantic import BaseModel, ValidationError

from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet_workflows.record_mapper import RecordMapper

# A 5k-row chunk with two mapped columns should stay comfortably below this
# threshold; a fully materialized 50k-row mapping regression would be
# substantially larger.
_STREAMING_PEAK_BYTES_LIMIT = 35_000_000


def test_dataframe_builds_expected_structure() -> None:
    """Test test_dataframe_builds_expected_structure behavior."""
    sdk = MagicMock()
    variables = [
        Variable(variable_name="VAR1", label="Label1", form_id=10),
        Variable(variable_name="VAR2", label="Label2", form_id=10),
    ]

    def var_list(**kwargs):
        """Test var_list behavior."""
        if kwargs.get("variableNames"):
            assert kwargs == {
                "study_key": "STUDY",
                "variableNames": ["VAR1"],
                "formIds": [10],
            }
            return [variables[0]]
        assert kwargs == {"study_key": "STUDY"}
        return variables

    sdk.get_variables.side_effect = var_list
    records = [
        Record(
            record_id=1,
            subject_key="S1",
            visit_id=1,
            form_id=10,
            record_status="Complete",
            date_created=datetime(2021, 1, 1),
            record_data={"VAR1": "a", "VAR2": "b"},
        )
    ]
    sdk.get_records.return_value = records

    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY", visit_key="1")

    sdk.get_variables.assert_called_once_with(study_key="STUDY")
    sdk.get_records.assert_called_once_with(
        study_key="STUDY",
        record_data_filter=None,
        visitId=1,
    )

    expected_columns = [
        "recordId",
        "subjectKey",
        "visitId",
        "formId",
        "recordStatus",
        "dateCreated",
        "Label1",
        "Label2",
    ]
    assert list(df.columns) == expected_columns
    assert df.iloc[0]["Label1"] == "a"
    assert df.iloc[0]["Label2"] == "b"


def test_dataframe_whitelists_variables_and_forms() -> None:
    """Test test_dataframe_whitelists_variables_and_forms behavior."""
    sdk = MagicMock()
    variables = [
        Variable(variable_name="VAR1", label="Label1", form_id=10),
        Variable(variable_name="VAR2", label="Label2", form_id=20),
    ]

    def var_list(**kwargs):
        """Test var_list behavior."""
        assert kwargs == {
            "study_key": "STUDY",
            "variableNames": ["VAR1"],
            "formIds": [10],
        }
        return [variables[0]]

    sdk.get_variables.side_effect = var_list
    record = Record(
        record_id=1,
        subject_key="S1",
        visit_id=1,
        form_id=10,
        record_status="Complete",
        date_created=datetime(2021, 1, 1),
        record_data={"VAR1": "a", "VAR2": "b"},
    )

    def rec_list(**kwargs):
        """Test rec_list behavior."""
        if kwargs.get("variableNames"):
            assert kwargs == {
                "study_key": "STUDY",
                "record_data_filter": None,
                "variableNames": ["VAR1"],
                "formIds": [10],
            }
            return [record]
        assert kwargs == {
            "study_key": "STUDY",
            "record_data_filter": None,
        }
        return [record]

    sdk.get_records.side_effect = rec_list

    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY", variable_whitelist=["VAR1"], form_whitelist=[10])

    sdk.get_variables.assert_called_once_with(
        study_key="STUDY",
        variableNames=["VAR1"],
        formIds=[10],
    )
    sdk.get_records.assert_called_once_with(
        study_key="STUDY",
        record_data_filter=None,
        variableNames=["VAR1"],
        formIds=[10],
    )
    assert list(df.columns) == [
        "recordId",
        "subjectKey",
        "visitId",
        "formId",
        "recordStatus",
        "dateCreated",
        "Label1",
    ]


def test_dataframe_empty_when_no_variables() -> None:
    """Test test_dataframe_empty_when_no_variables behavior."""
    sdk = MagicMock()
    sdk.get_variables.return_value = []
    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY")
    assert df.empty


def test_invalid_visit_key_logs_warning(caplog) -> None:
    """Test test_invalid_visit_key_logs_warning behavior."""
    sdk = MagicMock()
    sdk.get_variables.return_value = [Variable(variable_name="VAR", label="L", form_id=1)]
    sdk.get_records.return_value = []
    mapper = RecordMapper(sdk)

    with caplog.at_level("WARNING"):
        df = mapper.dataframe("S", visit_key="bad")

    assert df.empty
    assert "Invalid visit_key" in caplog.text
    sdk.get_records.assert_called_once_with(study_key="S", record_data_filter=None)


def test_records_fetch_error_returns_empty(caplog) -> None:
    """Test test_records_fetch_error_returns_empty behavior."""
    sdk = MagicMock()
    sdk.get_variables.return_value = [Variable(variable_name="VAR", label="L", form_id=1)]
    sdk.get_records.side_effect = Exception("boom")
    mapper = RecordMapper(sdk)

    with caplog.at_level("ERROR"):
        df = mapper.dataframe("S")

    assert df.empty
    assert "Failed to fetch records" in caplog.text


def test_parsing_error_logs_warning(monkeypatch, caplog) -> None:
    """Test test_parsing_error_logs_warning behavior."""
    sdk = MagicMock()
    sdk.get_variables.return_value = [Variable(variable_name="V", label="L", form_id=1)]
    record = Record(
        record_id=1,
        subject_key="S1",
        visit_id=1,
        form_id=1,
        record_status="Complete",
        date_created=datetime.now(),
        record_data={"V": "x"},
    )
    sdk.get_records.return_value = [record]

    class DummyModel(BaseModel):
        """Test suite for DummyModel."""

        def __init__(self, **kwargs):
            """Test __init__ behavior."""
            raise ValidationError([], DummyModel)

    monkeypatch.setattr("imednet_workflows.record_mapper.create_model", lambda *a, **k: DummyModel)

    mapper = RecordMapper(sdk)
    with caplog.at_level("WARNING"):
        df = mapper.dataframe("S")

    assert df.empty
    assert "Failed to parse record data" in caplog.text


def test_parse_records_counts_errors() -> None:
    """Test test_parse_records_counts_errors behavior."""
    mapper = RecordMapper(MagicMock())
    records = [
        Record(
            record_id=1,
            subject_key="S1",
            visit_id=1,
            form_id=1,
            record_status="Complete",
            date_created=datetime.now(),
            record_data={},
        ),
        Record(
            record_id=2,
            subject_key="S1",
            visit_id=1,
            form_id=1,
            record_status="Complete",
            date_created=datetime.now(),
            record_data={},
        ),
    ]

    class Dummy(BaseModel):
        """Test suite for Dummy."""

        def __init__(self, **_: Any) -> None:  # noqa: D401 - simple
            """Always fail."""
            raise ValidationError([], Dummy)

    rows, count = mapper._parse_records(records, Dummy)

    assert rows == []
    assert count == 2


def test_dataframe_raises_importerror_when_pandas_missing(monkeypatch) -> None:
    """Test test_dataframe_raises_importerror_when_pandas_missing behavior."""
    monkeypatch.setattr("imednet_workflows.record_mapper.pd", None)
    mapper = RecordMapper(MagicMock())
    with pytest.raises(ImportError, match="pandas is required for RecordMapper.dataframe"):
        mapper.dataframe("STUDY")


def test_iter_dataframes_streams_large_study_with_bounded_memory() -> None:
    """Test test_iter_dataframes_streams_large_study_with_bounded_memory behavior."""
    fake = Faker()

    class _StreamingLoader:
        """Test suite for _StreamingLoader."""

        def __init__(self) -> None:
            """Test __init__ behavior."""
            self.sync_records = MagicMock()

        def iter_cached_records(self, study_key: str, *, chunk_size: int = 5_000):
            """Test iter_cached_records behavior."""
            assert study_key == "STUDY"
            assert chunk_size == 5_000
            for record_id in range(50_000):
                yield Record(
                    study_key="STUDY",
                    record_id=record_id,
                    subject_key=f"S{record_id}",
                    visit_id=record_id % 5,
                    form_id=10,
                    form_key="LAB",
                    record_status="Complete",
                    date_created=datetime(2024, 1, 1),
                    record_data={
                        "AGE": fake.pyint(min_value=18, max_value=90),
                        "COMMENT": fake.lexify(text="????????"),
                    },
                )

    sdk = MagicMock()
    sdk.get_variables.return_value = [
        Variable(variable_name="AGE", label="Age", form_id=10),
        Variable(variable_name="COMMENT", label="Comment", form_id=10),
    ]
    loader = _StreamingLoader()
    mapper = RecordMapper(sdk, loader=loader, chunk_size=5_000)

    tracemalloc.start()
    chunk_sizes: list[int] = []
    peak_bytes = 0
    for frame in mapper.iter_dataframes("STUDY", use_labels_as_columns=False):
        chunk_sizes.append(len(frame))
        _, current_peak = tracemalloc.get_traced_memory()
        peak_bytes = max(peak_bytes, current_peak)
    tracemalloc.stop()

    loader.sync_records.assert_called_once_with("STUDY")
    assert chunk_sizes == [5_000] * 10
    assert peak_bytes < _STREAMING_PEAK_BYTES_LIMIT
