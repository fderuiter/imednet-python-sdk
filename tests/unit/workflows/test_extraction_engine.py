from __future__ import annotations

from datetime import datetime

from imednet.models import Record
from imednet.models.study_config import MappingRule, StudyConfiguration
from imednet_workflows.extraction_engine import extract_canonical_records


def test_extract_canonical_records_maps_ae_pd_dd_and_collects_row_errors() -> None:
    config = StudyConfiguration(
        study_key="STUDY-1",
        mappings=[
            MappingRule(
                domain="AE",
                target_field="subjectKey",
                source_form_key="AE_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="AE",
                target_field="aeTerm",
                source_form_key="AE_FORM",
                source_variable_name="recordData.ae.term",
            ),
            MappingRule(
                domain="AE",
                target_field="aeSeverity",
                source_form_key="AE_FORM",
                source_variable_name="recordData.ae.severity",
            ),
            MappingRule(
                domain="PD",
                target_field="subjectKey",
                source_form_key="PD_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="PD",
                target_field="dvTerm",
                source_form_key="PD_FORM",
                source_variable_name="recordData.dv.term",
            ),
            MappingRule(
                domain="PD",
                target_field="dvCategory",
                source_form_key="PD_FORM",
                source_variable_name="recordData.dv.category",
            ),
            MappingRule(
                domain="PD",
                target_field="dvSeverity",
                source_form_key="PD_FORM",
                source_variable_name="recordData.dv.severity",
            ),
            MappingRule(
                domain="PD",
                target_field="dvDate",
                source_form_key="PD_FORM",
                source_variable_name="recordData.dv.date",
            ),
            MappingRule(
                domain="DD",
                target_field="subjectKey",
                source_form_key="DD_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="DD",
                target_field="ddTerm",
                source_form_key="DD_FORM",
                source_variable_name="recordData.dd.term",
            ),
            MappingRule(
                domain="DD",
                target_field="ddCategory",
                source_form_key="DD_FORM",
                source_variable_name="recordData.dd.category",
            ),
            MappingRule(
                domain="DD",
                target_field="ddDate",
                source_form_key="DD_FORM",
                source_variable_name="recordData.dd.date",
            ),
        ],
    )

    records = [
        Record(
            record_id=1,
            form_key="AE_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 1),
            record_data={"ae": {"term": "Headache", "severity": "MILD"}},
        ),
        Record(
            record_id=2,
            form_key="PD_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 1),
            record_data={
                "dv": {
                    "term": "Missed visit",
                    "category": "PROCEDURE",
                    "severity": "MAJOR",
                    "date": "invalid-date-format",
                }
            },
        ),
        Record(
            record_id=3,
            form_key="DD_FORM",
            subject_key="SUBJ-002",
            date_created=datetime(2024, 1, 1),
            record_data={
                "dd": {
                    "term": "Battery failed",
                    "category": "HARDWARE",
                    "date": "2024-03-15T12:30:00+00:00",
                }
            },
        ),
        Record(
            record_id=4,
            form_key="OTHER_FORM",
            subject_key="SUBJ-003",
            date_created=datetime(2024, 1, 1),
            record_data={"foo": "bar"},
        ),
    ]

    result = extract_canonical_records(records=records, study_configuration=config)

    assert len(result.adverse_events) == 1
    assert result.adverse_events[0].subject_key == "SUBJ-001"
    assert result.adverse_events[0].ae_term == "Headache"

    assert len(result.protocol_deviations) == 0

    assert len(result.device_deficiencies) == 1
    assert result.device_deficiencies[0].subject_key == "SUBJ-002"
    assert result.device_deficiencies[0].dd_term == "Battery failed"

    assert len(result.validation_errors) == 1
    error = result.validation_errors[0]
    assert error["recordId"] == 2
    assert error["formKey"] == "PD_FORM"
    assert error["domain"] == "PD"
    assert error["payload"]["dvDate"] == "invalid-date-format"


def test_extract_canonical_records_uses_fallback_values() -> None:
    config = StudyConfiguration(
        study_key="STUDY-1",
        mappings=[
            MappingRule(
                domain="AE",
                target_field="subjectKey",
                source_form_key="AE_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="AE",
                target_field="aeTerm",
                source_form_key="AE_FORM",
                source_variable_name="recordData.term",
                fallback_value="Unknown event",
            ),
            MappingRule(
                domain="AE",
                target_field="aeSeverity",
                source_form_key="AE_FORM",
                source_variable_name="recordData.severity",
                fallback_value="MILD",
            ),
        ],
    )

    record = Record(
        record_id=5,
        form_key="AE_FORM",
        subject_key="SUBJ-010",
        date_created=datetime(2024, 1, 1),
        record_data={},
    )

    result = extract_canonical_records(records=[record], study_configuration=config)

    assert len(result.adverse_events) == 1
    assert result.adverse_events[0].ae_term == "Unknown event"
    assert result.adverse_events[0].ae_severity == "MILD"
    assert result.validation_errors == []
