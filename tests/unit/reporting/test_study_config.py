"""TODO: Add docstring."""
import pytest
from pydantic import ValidationError

from imednet.models.study_config import MappingRule, StudyConfiguration, WidgetConfig


def test_study_configuration_roundtrip_json_with_aliases() -> None:
    """TODO: Add docstring."""
    config = StudyConfiguration.model_validate(
        {
            "studyKey": " STUDY-001 ",
            "reportingProfile": " drug ",
            "mappings": [
                {
                    "domain": " AE ",
                    "targetField": " aeSeverity ",
                    "sourceFormKey": " FORM_AE ",
                    "sourceVariableName": " AE_SEV ",
                    "fallbackValue": " Unknown ",
                }
            ],
            "terminologyLookups": {"aeSeverity": {"MILD ": " Mild "}},
            "widgets": [
                {
                    "widgetId": " w-1 ",
                    "type": " bar_chart ",
                    "title": " AE Severity ",
                    "domain": " AE ",
                    "xAxis": " aeSeverity ",
                    "yAxis": " count ",
                    "layoutCols": 6,
                }
            ],
        }
    )

    payload_json = config.model_dump_json(by_alias=True)
    parsed = StudyConfiguration.model_validate_json(payload_json)

    assert parsed == config
    assert parsed.study_key == "STUDY-001"
    assert parsed.reporting_profile == "drug"
    assert parsed.mappings[0].domain == "AE"
    assert parsed.widgets[0].title == "AE Severity"
    assert parsed.terminology_lookups["aeSeverity"]["MILD"] == "Mild"
    assert "MILD " not in parsed.terminology_lookups["aeSeverity"]


def test_study_configuration_accepts_snake_case_field_names() -> None:
    """TODO: Add docstring."""
    config = StudyConfiguration(
        study_key="STUDY-002",
        mappings=[
            MappingRule(
                domain="PD",
                target_field="dvSeverity",
                source_form_key="FORM_PD",
                source_variable_name="DV_SEV",
            )
        ],
        widgets=[WidgetConfig(widget_id="kpi-1", type="kpi_card", title="PD", domain="PD")],
    )

    dumped = config.model_dump(by_alias=True)

    assert dumped["studyKey"] == "STUDY-002"
    assert dumped["version"] == "1.0.0"
    assert dumped["reportingProfile"] == "general"
    assert dumped["mappings"][0]["targetField"] == "dvSeverity"
    assert dumped["widgets"][0]["layoutCols"] == 12


def test_study_configuration_rejects_unknown_reporting_profile() -> None:
    """TODO: Add docstring."""
    with pytest.raises(ValidationError, match="reportingProfile must be one of"):
        StudyConfiguration.model_validate(
            {
                "studyKey": "STUDY-003",
                "reportingProfile": "custom",
            }
        )
