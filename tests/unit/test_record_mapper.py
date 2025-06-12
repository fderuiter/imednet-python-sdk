from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.workflows.record_mapper import RecordMapper


def test_dataframe_builds_expected_structure() -> None:
    sdk = MagicMock()
    variables = [
        Variable(variable_name="VAR1", label="Label1", form_id=10),
        Variable(variable_name="VAR2", label="Label2", form_id=10),
    ]
    sdk.variables.list.return_value = variables
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

    sdk.variables.list.assert_called_once_with(study_key="STUDY")
    sdk.records.list.assert_called_once_with(study_key="STUDY", filter="visitId==1")

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


def test_dataframe_empty_when_no_variables() -> None:
    sdk = MagicMock()
    sdk.variables.list.return_value = []
    mapper = RecordMapper(sdk)
    df = mapper.dataframe("STUDY")
    assert df.empty
