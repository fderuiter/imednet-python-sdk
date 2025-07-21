from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

from pydantic import BaseModel, ValidationError

from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.workflows.record_mapper import RecordMapper


def test_dataframe_builds_expected_structure() -> None:
    sdk = MagicMock()
    variables = [
        Variable(variable_name="VAR1", label="Label1", form_id=10),
        Variable(variable_name="VAR2", label="Label2", form_id=10),
    ]

    def var_list(**kwargs):
        if kwargs.get("variableNames"):
            assert kwargs == {
                "study_key": "STUDY",
                "variableNames": ["VAR1"],
                "formIds": [10],
            }
            return [variables[0]]
        assert kwargs == {"study_key": "STUDY", "variableNames": None, "formIds": None}
        return variables

    sdk.variables.list.side_effect = var_list
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
    sdk.records.list.return_value = records

    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY", visit_key="1")

    sdk.variables.list.assert_called_once_with(
        study_key="STUDY",
        variableNames=None,
        formIds=None,
    )
    sdk.records.list.assert_called_once_with(
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
    sdk = MagicMock()
    variables = [
        Variable(variable_name="VAR1", label="Label1", form_id=10),
        Variable(variable_name="VAR2", label="Label2", form_id=20),
    ]

    def var_list(**kwargs):
        assert kwargs == {
            "study_key": "STUDY",
            "variableNames": ["VAR1"],
            "formIds": [10],
        }
        return [variables[0]]

    sdk.variables.list.side_effect = var_list
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

    sdk.records.list.side_effect = rec_list

    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY", variable_whitelist=["VAR1"], form_whitelist=[10])

    sdk.variables.list.assert_called_once_with(
        study_key="STUDY",
        variableNames=["VAR1"],
        formIds=[10],
    )
    sdk.records.list.assert_called_once_with(
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
    sdk = MagicMock()
    sdk.variables.list.return_value = []
    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY")
    assert df.empty


def test_invalid_visit_key_logs_warning(caplog) -> None:
    sdk = MagicMock()
    sdk.variables.list.return_value = [Variable(variable_name="VAR", label="L", form_id=1)]
    sdk.records.list.return_value = []
    mapper = RecordMapper(sdk)

    with caplog.at_level("WARNING"):
        df = mapper.dataframe("S", visit_key="bad")

    assert df.empty
    assert "Invalid visit_key" in caplog.text
    sdk.records.list.assert_called_once_with(study_key="S", record_data_filter=None)


def test_records_fetch_error_returns_empty(caplog) -> None:
    sdk = MagicMock()
    sdk.variables.list.return_value = [Variable(variable_name="VAR", label="L", form_id=1)]
    sdk.records.list.side_effect = Exception("boom")
    mapper = RecordMapper(sdk)

    with caplog.at_level("ERROR"):
        df = mapper.dataframe("S")

    assert df.empty
    assert "Failed to fetch records" in caplog.text


def test_parsing_error_logs_warning(monkeypatch, caplog) -> None:
    sdk = MagicMock()
    sdk.variables.list.return_value = [Variable(variable_name="V", label="L", form_id=1)]
    record = Record(
        record_id=1,
        subject_key="S1",
        visit_id=1,
        form_id=1,
        record_status="Complete",
        date_created=datetime.now(),
        record_data={"V": "x"},
    )
    sdk.records.list.return_value = [record]

    class DummyModel(BaseModel):
        def __init__(self, **kwargs):
            raise ValidationError([], DummyModel)

    monkeypatch.setattr("imednet.workflows.record_mapper.create_model", lambda *a, **k: DummyModel)

    mapper = RecordMapper(sdk)
    with caplog.at_level("WARNING"):
        df = mapper.dataframe("S")

    assert df.empty
    assert "Failed to parse record data" in caplog.text


def test_parse_records_counts_errors() -> None:
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
        def __init__(self, **_: Any) -> None:  # noqa: D401 - simple
            """Always fail."""
            raise ValidationError([], Dummy)

    rows, count = mapper._parse_records(records, Dummy)

    assert rows == []
    assert count == 2
