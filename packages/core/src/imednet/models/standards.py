"""Data standard profiles and validation models for clinical domains."""

from __future__ import annotations

from typing import Any

from msgspec import Struct

from imednet.utils.validators import is_missing_value


class ValidationViolation(Struct, kw_only=True, omit_defaults=True):
    """Represents a violation of a data standard constraint."""

    field: str
    message: str
    severity: str  # ERROR, WARNING


class StandardsProfile:
    """A profile defining required, recommended, and optional fields for data domains."""

    def __init__(
        self,
        *,
        profile_name: str,
        required_fields: dict[str, list[str]] | None = None,
        recommended_fields: dict[str, list[str]] | None = None,
        optional_fields: dict[str, list[str]] | None = None,
        value_constraints: dict[str, list[Any]] | None = None,
    ) -> None:
        """Initialize a standards profile.

        Args:
            profile_name: Unique name for the profile.
            required_fields: Mapping of domain to required field names.
            recommended_fields: Mapping of domain to recommended field names.
            optional_fields: Mapping of domain to optional field names.
            value_constraints: Mapping of field or domain.field to allowed values.
        """
        self.profile_name = profile_name
        self.required_fields = required_fields or {}
        self.recommended_fields = recommended_fields or {}
        self.optional_fields = optional_fields or {}
        self.value_constraints = value_constraints or {}

    def expected_fields(self, domain: str) -> list[str]:
        """Return the list of expected (required + recommended) fields for a domain."""
        domain_key = domain.upper()
        return [
            *self.required_fields.get(domain_key, []),
            *self.recommended_fields.get(domain_key, []),
        ]

    def validate(self, domain: str, data: dict[str, Any]) -> list[ValidationViolation]:
        """Validate a data dictionary against the profile for a specific domain.

        Args:
            domain: The domain name (e.g., 'AE', 'PD').
            data: The data dictionary to validate.

        Returns:
            A list of ValidationViolation objects.
        """
        domain_key = domain.upper()
        violations: list[ValidationViolation] = []

        for field_name in self.required_fields.get(domain_key, []):
            if is_missing_value(data.get(field_name)):
                violations.append(
                    ValidationViolation(
                        field=field_name,
                        message=(
                            f"{field_name} is required for {domain_key} in {self.profile_name}."
                        ),
                        severity="ERROR",
                    )
                )

        for field_name in self.recommended_fields.get(domain_key, []):
            if is_missing_value(data.get(field_name)):
                violations.append(
                    ValidationViolation(
                        field=field_name,
                        message=(
                            f"{field_name} is recommended for {domain_key} in {self.profile_name}."
                        ),
                        severity="WARNING",
                    )
                )

        for constraint_key, allowed_values in self.value_constraints.items():
            if "." in constraint_key:
                constraint_domain, field_name = constraint_key.split(".", 1)
                if constraint_domain.upper() != domain_key:
                    continue
            else:
                field_name = constraint_key

            value = data.get(field_name)
            if is_missing_value(value):
                continue
            if value not in allowed_values:
                violations.append(
                    ValidationViolation(
                        field=field_name,
                        message=f"{field_name} must be one of {allowed_values}.",
                        severity="ERROR",
                    )
                )

        return violations


class GeneralClinicalProfile(StandardsProfile):
    """General clinical profile with basic AE and PD requirements."""

    def __init__(self) -> None:
        """Initialize the general clinical profile."""
        super().__init__(
            profile_name="general",
            required_fields={
                "AE": ["subjectKey", "aeTerm", "aeSeverity"],
                "PD": ["subjectKey", "dvTerm", "dvCategory", "dvSeverity", "dvDate"],
            },
            recommended_fields={
                "AE": ["aeDecod", "aeRelationship"],
                "PD": ["dvStatus"],
            },
            optional_fields={
                "DD": ["subjectKey", "ddTerm", "ddCategory", "ddDate", "ddSerious"],
            },
        )


class DrugSafetyProfile(StandardsProfile):
    """Drug safety profile with stricter requirements for AE data."""

    def __init__(self) -> None:
        """Initialize the drug safety profile."""
        super().__init__(
            profile_name="drug",
            required_fields={
                "AE": ["subjectKey", "aeTerm", "aeSeverity", "aeDecod", "aeRelationship"],
                "PD": ["subjectKey", "dvTerm", "dvCategory", "dvSeverity", "dvDate"],
            },
            recommended_fields={"AE": ["aeActionTaken", "aeOutcome"]},
            optional_fields={"DD": ["subjectKey", "ddTerm", "ddCategory", "ddDate", "ddSerious"]},
            value_constraints={"AE.aeSeverity": [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]},
        )


class DeviceSafetyProfile(StandardsProfile):
    """Device safety profile including device deficiency (DD) requirements."""

    def __init__(self) -> None:
        """Initialize the device safety profile."""
        super().__init__(
            profile_name="device",
            required_fields={
                "AE": ["subjectKey", "aeTerm", "aeSeverity"],
                "PD": ["subjectKey", "dvTerm", "dvCategory", "dvSeverity", "dvDate"],
                "DD": ["subjectKey", "ddTerm", "ddCategory", "ddDate", "ddSerious"],
            },
            recommended_fields={"DD": ["ddRelationship", "ddActionTaken"]},
            optional_fields={},
        )

    def validate(self, domain: str, data: dict[str, Any]) -> list[ValidationViolation]:
        """Validate device-specific constraints for DD and other domains."""
        violations = super().validate(domain=domain, data=data)
        domain_key = domain.upper()

        if domain_key != "DD":
            return violations

        deficiency_occurred = data.get("ddOccurred")
        if deficiency_occurred is True and all(
            is_missing_value(data.get(field_name))
            for field_name in ("ddTerm", "ddCategory", "ddDate")
        ):
            violations.append(
                ValidationViolation(
                    field="ddOccurred",
                    message="DD record details are required when ddOccurred is true.",
                    severity="ERROR",
                )
            )

        dd_serious = data.get("ddSerious")
        if not is_missing_value(dd_serious) and not isinstance(dd_serious, bool):
            violations.append(
                ValidationViolation(
                    field="ddSerious",
                    message="ddSerious must be a boolean value for device studies.",
                    severity="ERROR",
                )
            )

        return violations


class StandardsProfileRegistry:
    """Registry for managing and retrieving standards profiles."""

    def __init__(self) -> None:
        """Initialize an empty profile registry."""
        self._profiles: dict[str, StandardsProfile] = {}

    def register(self, profile: StandardsProfile) -> None:
        """Register a new standards profile."""
        self._profiles[profile.profile_name] = profile

    def get(self, profile_name: str) -> StandardsProfile:
        """Retrieve a profile by its name."""
        return self._profiles[profile_name]

    def list_profiles(self) -> list[str]:
        """List all registered profile names."""
        return sorted(self._profiles.keys())


PROFILE_REGISTRY = StandardsProfileRegistry()
PROFILE_REGISTRY.register(GeneralClinicalProfile())
PROFILE_REGISTRY.register(DrugSafetyProfile())
PROFILE_REGISTRY.register(DeviceSafetyProfile())


__all__ = [
    "ValidationViolation",
    "StandardsProfile",
    "GeneralClinicalProfile",
    "DrugSafetyProfile",
    "DeviceSafetyProfile",
    "StandardsProfileRegistry",
    "PROFILE_REGISTRY",
]
