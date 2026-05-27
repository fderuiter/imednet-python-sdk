from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from imednet.models.forms import Form
from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet_workflows.schema_profiler import SchemaProfiler


def test_schema_profiler_builds_form_and_field_profiles() -> None:
    sdk = MagicMock()
    sdk.forms.list.return_value = [Form(form_key="AE", form_name="Adverse Events", form_id=10)]
    sdk.variables.list.return_value = [
        Variable(
            form_id=10,
            form_key="AE",
            variable_name="AGE",
            label="Age",
            variable_type="integer",
        ),
        Variable(
            form_id=10,
            form_key="AE",
            variable_name="CONSENT_DATE",
            label="Consent Date",
            variable_type="date",
        ),
        Variable(
            form_id=10,
            form_key="AE",
            variable_name="SMOKER",
            label="Smoker",
            variable_type="boolean",
        ),
        Variable(
            form_id=10,
            form_key="AE",
            variable_name="COMMENT",
            label="Comment",
            variable_type="string",
        ),
    ]
    records = [
        Record(
            study_key="STUDY",
            form_id=10,
            form_key="AE",
            record_id=1,
            subject_key="S1",
            date_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
            record_data={
                "AGE": 34,
                "CONSENT_DATE": "2024-01-10",
                "SMOKER": True,
                "COMMENT": "baseline",
            },
        ),
        Record(
            study_key="STUDY",
            form_id=10,
            form_key="AE",
            record_id=2,
            subject_key="S2",
            date_modified=datetime(2024, 1, 2, tzinfo=timezone.utc),
            record_data={
                "AGE": None,
                "CONSENT_DATE": "2024-01-12",
                "SMOKER": False,
                "COMMENT": "",
                "EXTRA_FIELD": "investigator note",
            },
        ),
    ]

    profiler = SchemaProfiler(sdk)
    profiles = profiler.profile_records("STUDY", records=records)

    sdk.forms.list.assert_called_once_with(study_key="STUDY")
    sdk.variables.list.assert_called_once_with(study_key="STUDY")

    form_profile = profiles["AE"]
    assert form_profile.form_name == "Adverse Events"
    assert form_profile.record_count == 2
    assert form_profile.fields["AGE"].population_rate == 50.0
    assert form_profile.fields["AGE"].inferred_type == "numeric"
    assert form_profile.fields["AGE"].unique_values == ["34"]
    assert form_profile.fields["CONSENT_DATE"].inferred_type == "date"
    assert form_profile.fields["SMOKER"].inferred_type == "boolean"
    assert form_profile.fields["COMMENT"].population_rate == 50.0
    assert form_profile.fields["EXTRA_FIELD"].label == "EXTRA_FIELD"
    assert form_profile.fields["EXTRA_FIELD"].unique_count == 1


def test_schema_profiler_uses_loader_when_records_are_not_supplied() -> None:
    sdk = MagicMock()
    loader = MagicMock()
    loader.load_records.return_value = [
        Record(
            study_key="STUDY",
            form_id=10,
            form_key="LAB",
            record_id=1,
            subject_key="S1",
            date_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
            record_data={"RESULT": "7.2"},
        )
    ]
    sdk.forms.list.return_value = [Form(form_key="LAB", form_name="Labs", form_id=10)]
    sdk.variables.list.return_value = [
        Variable(
            form_id=10,
            form_key="LAB",
            variable_name="RESULT",
            label="Result",
            variable_type="float",
        )
    ]

    profiler = SchemaProfiler(sdk, loader=loader)
    profiles = profiler.profile_records("STUDY")

    loader.load_records.assert_called_once_with("STUDY")
    assert profiles["LAB"].fields["RESULT"].inferred_type == "numeric"


def test_schema_profiler_streams_chunked_loader_records() -> None:
    sdk = MagicMock()

    class _ChunkedLoader:
        def __init__(self) -> None:
            self.load_records = MagicMock()
            self._iter_mock = MagicMock()

        def iter_cached_records(self, study_key: str):
            self._iter_mock(study_key)
            return iter(
                [
                    Record(
                        study_key="STUDY",
                        form_id=10,
                        form_key="LAB",
                        record_id=1,
                        subject_key="S1",
                        date_modified=datetime(2024, 1, 1, tzinfo=timezone.utc),
                        record_data={"RESULT": "7.2"},
                    ),
                    Record(
                        study_key="STUDY",
                        form_id=10,
                        form_key="LAB",
                        record_id=2,
                        subject_key="S2",
                        date_modified=datetime(2024, 1, 2, tzinfo=timezone.utc),
                        record_data={"RESULT": "8.1"},
                    ),
                ]
            )

    loader = _ChunkedLoader()
    sdk.forms.list.return_value = [Form(form_key="LAB", form_name="Labs", form_id=10)]
    sdk.variables.list.return_value = [
        Variable(
            form_id=10,
            form_key="LAB",
            variable_name="RESULT",
            label="Result",
            variable_type="float",
        )
    ]

    profiler = SchemaProfiler(sdk, loader=loader)
    profile = profiler.profile_records("STUDY")["LAB"]

    loader.load_records.assert_called_once_with("STUDY")
    loader._iter_mock.assert_called_once_with("STUDY")
    assert profile.record_count == 2
    assert profile.fields["RESULT"].population_rate == 100.0
