"""Test Standards Validation module."""

import pytest

from imednet.models.standards import DrugSafetyProfile
from imednet_workflows.standards_validation import (
    CategoricalNormalizer,
    StandardsReadinessValidator,
)


def test_categorical_normalizer_translates_lookup_values_and_yes_no_booleans() -> None:
    """Test the test categorical normalizer translates lookup values and yes no booleans functionality."""
    normalizer = CategoricalNormalizer()
    result = normalizer.normalize_record(
        {
            "subjectKey": "S004",
            "AE_SEV": "2",
            "aeSerious": "YES",
        },
        terminology_lookups={"AE_SEV": {"1": "MILD", "2": "MODERATE", "3": "SEVERE"}},
    )

    assert result.normalized_record["AE_SEV"] == "MODERATE"
    assert result.normalized_record["aeSerious"] is True
    assert result.warnings == []


def test_standards_readiness_validator_scores_records() -> None:
    """Test the test standards readiness validator scores records functionality."""
    validator = StandardsReadinessValidator(profile=DrugSafetyProfile())
    report = validator.score_records(
        records_by_domain={
            "AE": [
                {
                    "subjectKey": "S001",
                    "aeTerm": "Headache",
                    "aeSeverity": "3",
                    "aeDecod": "HEADACHE",
                    "aeRelationship": "RELATED",
                    "aeActionTaken": "NONE",
                    "aeOutcome": "RECOVERED",
                },
                {
                    "subjectKey": "S004",
                    "aeTerm": "Nausea",
                    "aeSeverity": "9",
                    "aeDecod": "",
                    "aeRelationship": "",
                },
            ]
        },
        terminology_lookups={"aeSeverity": {"1": "1", "2": "2", "3": "3", "4": "4", "5": "5"}},
    )

    assert report.total_expected_fields == 14
    assert report.successfully_validated_fields == 9
    assert report.score == pytest.approx((9 / 14) * 100)
    assert "Subject S004 record aeSeverity is unmapped" in report.warnings
    assert {(violation.field, violation.severity) for violation in report.violations} == {
        ("aeActionTaken", "WARNING"),
        ("aeDecod", "ERROR"),
        ("aeOutcome", "WARNING"),
        ("aeRelationship", "ERROR"),
        ("aeSeverity", "ERROR"),
    }
