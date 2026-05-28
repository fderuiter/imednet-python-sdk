from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError

from imednet.spi.models import (
    AdverseEvent,
    DeviceDeficiency,
    MappingRule,
    ProtocolDeviation,
    Record,
    StudyConfiguration,
)

_DOMAIN_MODEL_MAP = {
    "AE": AdverseEvent,
    "PD": ProtocolDeviation,
    "DD": DeviceDeficiency,
}


class ExtractionResult(BaseModel):
    """Canonical extraction output grouped by reporting domain."""

    adverse_events: list[AdverseEvent] = Field(default_factory=list)
    protocol_deviations: list[ProtocolDeviation] = Field(default_factory=list)
    device_deficiencies: list[DeviceDeficiency] = Field(default_factory=list)
    validation_errors: list[dict[str, Any]] = Field(default_factory=list)


def _get_from_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
        else:
            return None
    return current


def _extract_rule_value_from_payload(
    record: Record, rule: MappingRule, top_level_payload: dict[str, Any]
) -> Any:
    source_path = rule.source_variable_name

    if source_path.startswith("recordData."):
        return _get_from_path(record.record_data, source_path[len("recordData.") :])

    if source_path.startswith("record_data."):
        return _get_from_path(record.record_data, source_path[len("record_data.") :])

    value = _get_from_path(top_level_payload, source_path)
    if value is not None:
        return value

    if "." not in source_path and isinstance(record.record_data, dict):
        return record.record_data.get(source_path)

    return None


def _is_missing_value(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value == "")


def _group_mappings_by_domain_and_form(
    study_configuration: StudyConfiguration,
) -> dict[str, dict[str, list[MappingRule]]]:
    grouped: dict[str, dict[str, list[MappingRule]]] = {}
    for rule in study_configuration.mappings:
        domain_key = rule.domain.upper()
        if domain_key not in _DOMAIN_MODEL_MAP:
            continue
        grouped.setdefault(domain_key, {}).setdefault(rule.source_form_key, []).append(rule)
    return grouped


def extract_canonical_records(
    records: list[Record], study_configuration: StudyConfiguration
) -> ExtractionResult:
    """Extract canonical AE/PD/DD models from raw records using study mappings."""
    result = ExtractionResult()
    grouped_mappings = _group_mappings_by_domain_and_form(study_configuration)

    for record in records:
        top_level_payload = {
            **record.model_dump(by_alias=False),
            **record.model_dump(by_alias=True),
        }
        for domain, by_form in grouped_mappings.items():
            rules = by_form.get(record.form_key)
            if not rules:
                continue

            payload: dict[str, Any] = {}
            for rule in rules:
                value = _extract_rule_value_from_payload(record, rule, top_level_payload)
                if _is_missing_value(value) and rule.fallback_value is not None:
                    value = rule.fallback_value
                payload[rule.target_field] = value

            model_type = _DOMAIN_MODEL_MAP[domain]
            try:
                model_instance = model_type(**payload)
            except ValidationError as exc:
                result.validation_errors.append(
                    {
                        "recordId": record.record_id,
                        "formKey": record.form_key,
                        "domain": domain,
                        "payload": payload,
                        "errors": exc.errors(),
                    }
                )
                continue

            if domain == "AE":
                result.adverse_events.append(model_instance)
            elif domain == "PD":
                result.protocol_deviations.append(model_instance)
            else:
                result.device_deficiencies.append(model_instance)

    return result


__all__ = ["ExtractionResult", "extract_canonical_records"]
