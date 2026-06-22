"""TODO: Add docstring."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from imednet.models.reporting import AdverseEvent, DeviceDeficiency, ProtocolDeviation


def test_adverse_event_parses_alias_input_and_coerces_types() -> None:
    """TODO: Add docstring."""
    model = AdverseEvent.model_validate(
        {
            "subjectKey": 101,
            "aeTerm": "  Headache  ",
            "aeSeverity": "MILD",
            "aeSerious": "1",
            "aeStartDate": "2024-01-01T10:00:00+00:00",
            "aeEndDate": "2024-01-02T10:00:00+00:00",
        }
    )

    assert model.subject_key == "101"
    assert model.ae_term == "Headache"
    assert model.ae_serious is True
    assert model.ae_start_date == datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert model.model_dump(by_alias=True)["subjectKey"] == "101"


def test_protocol_deviation_applies_defaults_and_parses_datetime_timestamp() -> None:
    """TODO: Add docstring."""
    model = ProtocolDeviation.model_validate(
        {
            "subjectKey": 77,
            "dvTerm": "Missed visit",
            "dvCategory": "PROCEDURE",
            "dvSeverity": "MAJOR",
            "dvDate": 1705309200,
        }
    )

    assert model.subject_key == "77"
    assert model.dv_status == "Unreviewed"
    assert model.dv_date == datetime(2024, 1, 15, 9, 0, tzinfo=timezone.utc)


def test_device_deficiency_parses_valid_input() -> None:
    """TODO: Add docstring."""
    model = DeviceDeficiency.model_validate(
        {
            "subjectKey": "SUBJ-001",
            "ddTerm": "Battery failed",
            "ddCategory": "HARDWARE",
            "ddDate": "2024-03-15T12:30:00+00:00",
            "ddSerious": "false",
        }
    )

    assert model.dd_serious is False
    assert model.dd_date == datetime(2024, 3, 15, 12, 30, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("model_cls", "payload"),
    [
        (AdverseEvent, {"aeTerm": "Headache", "aeSeverity": "MILD"}),
        (
            ProtocolDeviation,
            {
                "subjectKey": "SUBJ-1",
                "dvCategory": "PROCEDURE",
                "dvSeverity": "MAJOR",
                "dvDate": "2024-01-15T09:00:00+00:00",
            },
        ),
        (
            DeviceDeficiency,
            {
                "subjectKey": "SUBJ-1",
                "ddTerm": "Battery failed",
                "ddDate": "2024-01-15T09:00:00+00:00",
            },
        ),
    ],
)
def test_reporting_models_reject_missing_required_fields(model_cls: type, payload: dict) -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError):
        model_cls.model_validate(payload)


def test_protocol_deviation_rejects_invalid_datetime() -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError):
        ProtocolDeviation.model_validate(
            {
                "subjectKey": "SUBJ-1",
                "dvTerm": "Missed visit",
                "dvCategory": "PROCEDURE",
                "dvSeverity": "MAJOR",
                "dvDate": "not-a-datetime",
            }
        )
