from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from imednet.models.standards import StandardsProfile, ValidationViolation
from imednet.utils.validators import parse_bool


def _is_missing_value(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


class NormalizationResult(BaseModel):
    normalized_record: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)


class CategoricalNormalizer:
    def normalize_record(
        self,
        record: dict[str, Any],
        *,
        terminology_lookups: dict[str, dict[str, str]],
    ) -> NormalizationResult:
        normalized_record: dict[str, Any] = {}
        warnings: list[str] = []

        subject_key = record.get("subjectKey") or record.get("subject_key")
        for field_name, raw_value in record.items():
            normalized_value, warning_message = self._normalize_value(
                field_name=field_name,
                raw_value=raw_value,
                terminology_lookups=terminology_lookups,
                subject_key=subject_key,
            )
            normalized_record[field_name] = normalized_value
            if warning_message is not None:
                warnings.append(warning_message)

        return NormalizationResult(normalized_record=normalized_record, warnings=warnings)

    def _normalize_value(
        self,
        *,
        field_name: str,
        raw_value: Any,
        terminology_lookups: dict[str, dict[str, str]],
        subject_key: Any,
    ) -> tuple[Any, str | None]:
        lookup = terminology_lookups.get(field_name)
        if lookup and isinstance(raw_value, str):
            normalized_lookup = {str(key).strip().upper(): value for key, value in lookup.items()}
            lookup_key = raw_value.strip().upper()
            if lookup_key in normalized_lookup:
                return normalized_lookup[lookup_key], None
            subject_prefix = (
                f"Subject {subject_key} " if isinstance(subject_key, str) and subject_key else ""
            )
            return raw_value, f"{subject_prefix}record {field_name} is unmapped"

        if isinstance(raw_value, str):
            stripped_value = raw_value.strip()
            if stripped_value:
                parsed_bool = parse_bool(stripped_value)
                if stripped_value.lower() in {
                    "true",
                    "false",
                    "1",
                    "0",
                    "yes",
                    "no",
                    "y",
                    "n",
                    "t",
                    "f",
                }:
                    return parsed_bool, None

        return raw_value, None


class StandardsReadinessReport(BaseModel):
    score: float
    successfully_validated_fields: int
    total_expected_fields: int
    warnings: list[str] = Field(default_factory=list)
    violations: list[ValidationViolation] = Field(default_factory=list)


class StandardsReadinessValidator:
    def __init__(
        self, profile: StandardsProfile, normalizer: CategoricalNormalizer | None = None
    ) -> None:
        self._profile = profile
        self._normalizer = normalizer or CategoricalNormalizer()

    def score_records(
        self,
        *,
        records_by_domain: dict[str, list[dict[str, Any]]],
        terminology_lookups: dict[str, dict[str, str]] | None = None,
    ) -> StandardsReadinessReport:
        lookups = terminology_lookups or {}
        warnings: list[str] = []
        violations: list[ValidationViolation] = []
        successfully_validated_fields = 0
        total_expected_fields = 0

        for domain, records in records_by_domain.items():
            expected_fields = self._profile.expected_fields(domain)
            for record in records:
                normalization_result = self._normalizer.normalize_record(
                    record, terminology_lookups=lookups
                )
                warnings.extend(normalization_result.warnings)

                record_violations = self._profile.validate(
                    domain=domain, data=normalization_result.normalized_record
                )
                violations.extend(record_violations)

                total_expected_fields += len(expected_fields)
                error_fields = {
                    violation.field
                    for violation in record_violations
                    if violation.severity.upper() == "ERROR"
                }
                for field_name in expected_fields:
                    value = normalization_result.normalized_record.get(field_name)
                    if field_name in error_fields or _is_missing_value(value):
                        continue
                    successfully_validated_fields += 1

        score = (
            100.0
            if total_expected_fields == 0
            else (successfully_validated_fields / total_expected_fields) * 100
        )
        return StandardsReadinessReport(
            score=score,
            successfully_validated_fields=successfully_validated_fields,
            total_expected_fields=total_expected_fields,
            warnings=warnings,
            violations=violations,
        )


__all__ = [
    "CategoricalNormalizer",
    "NormalizationResult",
    "StandardsReadinessReport",
    "StandardsReadinessValidator",
]
