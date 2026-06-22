"""TODO: Add docstring."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from imednet.utils.validators import is_missing_value


class ValidationViolation(BaseModel):
    """TODO: Add docstring."""
    field: str
    message: str
    severity: str  # ERROR, WARNING


class StandardsProfile:
    """TODO: Add docstring."""
    def __init__(
        self,
        *,
        profile_name: str,
        required_fields: dict[str, list[str]] | None = None,
        recommended_fields: dict[str, list[str]] | None = None,
        optional_fields: dict[str, list[str]] | None = None,
        value_constraints: dict[str, list[Any]] | None = None,
    ) -> None:
        """TODO: Add docstring."""
        self.profile_name = profile_name
        self.required_fields = required_fields or {}
        self.recommended_fields = recommended_fields or {}
        self.optional_fields = optional_fields or {}
        self.value_constraints = value_constraints or {}

    def expected_fields(self, domain: str) -> list[str]:
        """TODO: Add docstring."""
        domain_key = domain.upper()
        return [
            *self.required_fields.get(domain_key, []),
            *self.recommended_fields.get(domain_key, []),
        ]

    def validate(self, domain: str, data: dict[str, Any]) -> list[ValidationViolation]:
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    def __init__(self) -> None:
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    def __init__(self) -> None:
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    def __init__(self) -> None:
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
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
    """TODO: Add docstring."""
    def __init__(self) -> None:
        """TODO: Add docstring."""
        self._profiles: dict[str, StandardsProfile] = {}

    def register(self, profile: StandardsProfile) -> None:
        """TODO: Add docstring."""
        self._profiles[profile.profile_name] = profile

    def get(self, profile_name: str) -> StandardsProfile:
        """TODO: Add docstring."""
        return self._profiles[profile_name]

    def list_profiles(self) -> list[str]:
        """TODO: Add docstring."""
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
