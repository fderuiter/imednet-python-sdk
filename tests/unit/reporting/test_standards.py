"""Test Standards module."""

from imednet.models.standards import (
    PROFILE_REGISTRY,
    DeviceSafetyProfile,
    DrugSafetyProfile,
    GeneralClinicalProfile,
)


def test_profile_registry_contains_general_drug_and_device_profiles() -> None:
    """Test the test profile registry contains general drug and device profiles functionality."""
    assert PROFILE_REGISTRY.list_profiles() == ["device", "drug", "general"]


def test_drug_profile_enforces_ae_decod_relationship_and_ctcae_grades() -> None:
    """Test the test drug profile enforces ae decod relationship and ctcae grades functionality."""
    profile = DrugSafetyProfile()
    violations = profile.validate(
        domain="AE",
        data={
            "subjectKey": "S001",
            "aeTerm": "Headache",
            "aeSeverity": "SEVERE",
        },
    )

    assert {(violation.field, violation.severity) for violation in violations} == {
        ("aeDecod", "ERROR"),
        ("aeRelationship", "ERROR"),
        ("aeSeverity", "ERROR"),
        ("aeActionTaken", "WARNING"),
        ("aeOutcome", "WARNING"),
    }


def test_general_profile_only_warns_for_missing_recommended_ae_fields() -> None:
    """Test the test general profile only warns for missing recommended ae fields functionality."""
    profile = GeneralClinicalProfile()
    violations = profile.validate(
        domain="AE",
        data={
            "subjectKey": "S001",
            "aeTerm": "Headache",
            "aeSeverity": "SEVERE",
        },
    )

    assert {(violation.field, violation.severity) for violation in violations} == {
        ("aeDecod", "WARNING"),
        ("aeRelationship", "WARNING"),
    }


def test_device_profile_requires_boolean_dd_serious() -> None:
    """Test the test device profile requires boolean dd serious functionality."""
    profile = DeviceSafetyProfile()
    violations = profile.validate(
        domain="DD",
        data={
            "subjectKey": "S002",
            "ddTerm": "Battery failed",
            "ddCategory": "HARDWARE",
            "ddDate": "2024-03-15T12:30:00+00:00",
            "ddSerious": "yes",
        },
    )

    assert {(violation.field, violation.severity) for violation in violations} == {
        ("ddActionTaken", "WARNING"),
        ("ddRelationship", "WARNING"),
        ("ddSerious", "ERROR"),
    }
