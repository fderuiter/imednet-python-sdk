"""TODO: Add docstring."""

from imednet.models.standards import (
    PROFILE_REGISTRY,
    DeviceSafetyProfile,
    DrugSafetyProfile,
    GeneralClinicalProfile,
)


def test_profile_registry_contains_general_drug_and_device_profiles() -> None:
    """TODO: Add docstring."""
    assert PROFILE_REGISTRY.list_profiles() == ["device", "drug", "general"]


def test_drug_profile_enforces_ae_decod_relationship_and_ctcae_grades() -> None:
    """TODO: Add docstring."""
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
    """TODO: Add docstring."""
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
    """TODO: Add docstring."""
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
