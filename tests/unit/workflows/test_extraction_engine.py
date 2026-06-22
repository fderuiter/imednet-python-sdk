"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime

from imednet.models import Record
from imednet.models.study_config import MappingRule, StudyConfiguration
from imednet_workflows.extraction_engine import extract_canonical_records


def test_extract_canonical_records_maps_ae_pd_dd_and_collects_row_errors() -> None:
    """TODO: Add docstring."""
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
    """TODO: Add docstring."""
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


def test_extract_subject_centric_analysis_datasets() -> None:
    """TODO: Add docstring."""
    config = StudyConfiguration(
        study_key="STUDY-2",
        mappings=[
            # ADSL Mapping
            MappingRule(
                domain="ADSL",
                target_field="subjectKey",
                source_form_key="DM_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="ADSL",
                target_field="age",
                source_form_key="DM_FORM",
                source_variable_name="recordData.dm.age",
            ),
            MappingRule(
                domain="ADSL",
                target_field="firstDoseDate",
                source_form_key="EX_FORM",
                source_variable_name="recordData.ex.startDate",
                businessLogic="value",
            ),
            # ADAE Mapping
            MappingRule(
                domain="ADAE",
                target_field="subjectKey",
                source_form_key="AE_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="ADAE",
                target_field="aeTerm",
                source_form_key="AE_FORM",
                source_variable_name="recordData.ae.term",
            ),
            MappingRule(
                domain="ADAE",
                target_field="treatmentEmergent",
                source_form_key="AE_FORM",
                source_variable_name="",
                businessLogic="record.record_data.get('ae', {}).get('startDate', '') >= state.get('ADSL.firstDoseDate', '9999-99-99')",
            ),
            # ADLB Mapping - Baseline and Change
            MappingRule(
                domain="ADLB",
                target_field="subjectKey",
                source_form_key="LB_FORM",
                source_variable_name="subjectKey",
            ),
            MappingRule(
                domain="ADLB",
                target_field="labTest",
                source_form_key="LB_FORM",
                source_variable_name="recordData.lb.test",
            ),
            MappingRule(
                domain="ADLB",
                target_field="result",
                source_form_key="LB_FORM",
                source_variable_name="recordData.lb.result",
                isBaseline=True,
                businessLogic="value if record.record_data.get('lb', {}).get('visit') == 'Baseline' else value",
            ),
            MappingRule(
                domain="ADLB",
                target_field="changeFromBaseline",
                source_form_key="LB_FORM",
                source_variable_name="",
                businessLogic="float(payload.get('result', 0)) - float(baseline.get('ADLB.result', 0)) if 'ADLB.result' in baseline and record.record_data.get('lb', {}).get('visit') != 'Baseline' else None",
            ),
        ],
    )

    records = [
        Record(
            record_id=1,
            form_key="DM_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 1),
            record_data={"dm": {"age": 45}},
        ),
        Record(
            record_id=2,
            form_key="EX_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 2),
            record_data={"ex": {"startDate": "2024-02-01"}},
        ),
        Record(
            record_id=3,
            form_key="AE_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 3),
            record_data={"ae": {"term": "Nausea", "startDate": "2024-02-05"}},
        ),
        Record(
            record_id=4,
            form_key="AE_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 4),
            record_data={
                "ae": {"term": "Headache", "startDate": "2024-01-15"}
            },  # before first dose
        ),
        Record(
            record_id=5,
            form_key="LB_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 5),
            record_data={"lb": {"test": "ALT", "result": 40.0, "visit": "Baseline"}},
        ),
        Record(
            record_id=6,
            form_key="LB_FORM",
            subject_key="SUBJ-001",
            date_created=datetime(2024, 1, 6),
            record_data={"lb": {"test": "ALT", "result": 55.0, "visit": "Visit 2"}},
        ),
    ]

    result = extract_canonical_records(records=records, study_configuration=config)

    assert len(result.adsl_records) == 1
    adsl = result.adsl_records[0].model_dump(by_alias=True)
    assert adsl["subjectKey"] == "SUBJ-001"
    assert adsl["age"] == 45
    assert adsl["firstDoseDate"] == "2024-02-01"

    assert len(result.adae_records) == 2
    adae1 = result.adae_records[0].model_dump(by_alias=True)
    assert adae1["aeTerm"] == "Nausea"
    assert adae1["treatmentEmergent"] is True

    adae2 = result.adae_records[1].model_dump(by_alias=True)
    assert adae2["aeTerm"] == "Headache"
    assert adae2["treatmentEmergent"] is False

    assert len(result.adlb_records) == 2
    adlb1 = result.adlb_records[0].model_dump(by_alias=True)
    assert adlb1["labTest"] == "ALT"
    assert adlb1["result"] == 40.0
    assert adlb1["changeFromBaseline"] is None

    adlb2 = result.adlb_records[1].model_dump(by_alias=True)
    assert adlb2["labTest"] == "ALT"
    assert adlb2["result"] == 55.0
    assert adlb2["changeFromBaseline"] == 15.0
