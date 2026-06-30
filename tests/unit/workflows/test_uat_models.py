"""TODO: Add docstring."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from faker import Faker
from pydantic import ValidationError

import imednet_workflows.uat.models as uat_models
from imednet_workflows.uat import (
    RecordTestType,
    UATFormSpec,
    UATSpecification,
    UATSubjectSpec,
    UATVariableSpec,
    VariableTestStrategy,
)

fake = Faker()


def _build_valid_spec() -> UATSpecification:
    """TODO: Add docstring."""
    variable = UATVariableSpec(
        variable_name="SYSTOLIC",
        variable_key="VAR-1",
        variable_type="Number",
        form_key="VITALS",
    )
    form = UATFormSpec(
        form_key="VITALS",
        form_name="Vitals",
        form_type="CRF",
        test_type=RecordTestType.CREATE_NEW_RECORD,
        variables=[variable],
        subject_count=1,
    )
    subject = UATSubjectSpec(site_name="Main Site", subject_count=1)
    return UATSpecification(
        study_key=fake.bothify(text="STUDY-####"),
        study_name=fake.company(),
        generated_at=datetime(2026, 1, 1, 0, 0, 0),
        subject_specs=[subject],
        form_specs=[form],
    )


def test_json_round_trip_serialization() -> None:
    """TODO: Add docstring."""
    spec = _build_valid_spec()
    payload = spec.model_dump_json()
    parsed = UATSpecification.model_validate_json(payload)
    assert parsed == spec


def test_alias_dump_uses_camel_case() -> None:
    """TODO: Add docstring."""
    spec = _build_valid_spec()
    payload = spec.model_dump(by_alias=True)
    assert "studyKey" in payload
    assert "formSpecs" in payload
    assert "subjectSpecs" in payload
    assert "generatedAt" in payload


def test_fixed_strategy_requires_fixed_value() -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError, match="fixed_value must be provided"):
        UATVariableSpec(
            variable_name="AGE",
            variable_key="AGE",
            variable_type="Number",
            form_key="DEMOG",
            strategy=VariableTestStrategy.FIXED,
        )


@pytest.mark.parametrize("count", [0, 101])
def test_subject_count_bounds(count: int) -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError, match="subject_count must be between 1 and 100"):
        UATFormSpec(
            form_key="DEMOG",
            form_name="Demographics",
            form_type="CRF",
            test_type=RecordTestType.CREATE_NEW_RECORD,
            subject_count=count,
        )
    with pytest.raises(ValidationError, match="subject_count must be between 1 and 100"):
        UATSubjectSpec(site_name="Main Site", subject_count=count)


def test_spec_version_is_pinned() -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError, match="spec_version must be '1.0'"):
        UATSpecification(
            spec_version="2.0",
            study_key="S1",
            study_name="Study",
        )


def test_variables_must_have_unique_names() -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError, match="duplicate variable_name"):
        UATFormSpec(
            form_key="LABS",
            form_name="Labs",
            form_type="CRF",
            test_type=RecordTestType.CREATE_NEW_RECORD,
            variables=[
                UATVariableSpec(
                    variable_name="HEMOGLOBIN",
                    variable_key="HGB-1",
                    variable_type="Number",
                    form_key="LABS",
                ),
                UATVariableSpec(
                    variable_name="HEMOGLOBIN",
                    variable_key="HGB-2",
                    variable_type="Number",
                    form_key="LABS",
                ),
            ],
        )


def test_enabled_forms_and_forms_by_type_filters_correctly() -> None:
    """TODO: Add docstring."""
    enabled_register = UATFormSpec(
        form_key="SUBJECT",
        form_name="Subject Registration",
        form_type="CRF",
        test_type=RecordTestType.REGISTER_SUBJECT,
    )
    disabled_register = UATFormSpec(
        form_key="SUBJECT-2",
        form_name="Subject Registration Copy",
        form_type="CRF",
        test_type=RecordTestType.REGISTER_SUBJECT,
        enabled=False,
    )
    enabled_create = UATFormSpec(
        form_key="LABS",
        form_name="Labs",
        form_type="CRF",
        test_type=RecordTestType.CREATE_NEW_RECORD,
    )
    spec = UATSpecification(
        study_key="S1",
        study_name="Study",
        form_specs=[enabled_register, disabled_register, enabled_create],
    )
    assert spec.enabled_forms() == [enabled_register, enabled_create]
    assert spec.forms_by_type(RecordTestType.REGISTER_SUBJECT) == [enabled_register]


def test_from_json_loads_correctly(tmp_path: Path) -> None:
    """TODO: Add docstring."""
    json_file = tmp_path / "spec.json"
    json_file.write_text(
        '{"specVersion": "1.0", "studyKey": "S1", "studyName": "Study", "formSpecs": [], "subjectSpecs": []}',
        encoding="utf-8",
    )

    spec = UATSpecification.from_json(json_file)
    assert spec.study_key == "S1"
