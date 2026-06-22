"""TODO: Add docstring."""

from __future__ import annotations

import collections
import logging
from typing import Any, cast

from pydantic import BaseModel, Field, ValidationError

from imednet.spi.models import (
    AdverseEvent,
    AnalysisAdverseEvent,
    AnalysisLabResult,
    DeviceDeficiency,
    MappingRule,
    ProtocolDeviation,
    Record,
    StudyConfiguration,
    SubjectLevelAnalysis,
)

logger = logging.getLogger(__name__)

_DOMAIN_MODEL_MAP = {
    "AE": AdverseEvent,
    "PD": ProtocolDeviation,
    "DD": DeviceDeficiency,
    "ADSL": SubjectLevelAnalysis,
    "ADAE": AnalysisAdverseEvent,
    "ADLB": AnalysisLabResult,
}


class ExtractionResult(BaseModel):
    """Canonical extraction output grouped by reporting domain."""

    adverse_events: list[AdverseEvent] = Field(default_factory=list)
    protocol_deviations: list[ProtocolDeviation] = Field(default_factory=list)
    device_deficiencies: list[DeviceDeficiency] = Field(default_factory=list)
    adsl_records: list[SubjectLevelAnalysis] = Field(default_factory=list)
    adae_records: list[AnalysisAdverseEvent] = Field(default_factory=list)
    adlb_records: list[AnalysisLabResult] = Field(default_factory=list)
    validation_errors: list[dict[str, Any]] = Field(default_factory=list)


def _get_from_path(value: Any, path: str) -> Any:
    """TODO: Add docstring."""
    if not path:
        return None
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
    """TODO: Add docstring."""
    source_path = rule.source_variable_name
    if not source_path:
        return None

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
    """TODO: Add docstring."""
    return value is None or (isinstance(value, str) and value == "")


def _group_mappings_by_domain_and_form(
    study_configuration: StudyConfiguration,
) -> dict[str, dict[str, list[MappingRule]]]:
    """TODO: Add docstring."""
    grouped: dict[str, dict[str, list[MappingRule]]] = {}
    for rule in study_configuration.mappings:
        domain_key = rule.domain.upper()
        if domain_key not in _DOMAIN_MODEL_MAP:
            continue
        grouped.setdefault(domain_key, {}).setdefault(rule.source_form_key, []).append(rule)
    return grouped


class SubjectContext:
    """TODO: Add docstring."""

    def __init__(self, subject_key: str):
        """TODO: Add docstring."""
        self.subject_key = subject_key
        self.state: dict[str, Any] = {}
        self.baseline: dict[str, Any] = {}


def _evaluate_business_logic(
    logic: str, record: Record, payload: dict[str, Any], context: SubjectContext, value: Any = None
) -> Any:
    """TODO: Add docstring."""
    try:
        # evaluate safely
        env = {
            "record": record,
            "payload": payload,
            "context": context,
            "state": context.state,
            "baseline": context.baseline,
            "subject_key": context.subject_key,
            "value": value,
        }
        builtins = {
            "float": float,
            "int": int,
            "str": str,
            "bool": bool,
            "len": len,
        }
        return eval(logic, {"__builtins__": builtins}, env)  # nosec B307  # nosem
    except Exception as e:
        logger.warning(f"Derivation logic failed for {context.subject_key}: {e}")
        return None


def extract_canonical_records(
    records: list[Record], study_configuration: StudyConfiguration
) -> ExtractionResult:
    """Extract canonical models from raw records using study mappings."""
    result = ExtractionResult()
    grouped_mappings = _group_mappings_by_domain_and_form(study_configuration)

    # Subject-centric processing: group records by subject, sort chronologically
    subject_records: dict[str, list[Record]] = collections.defaultdict(list)
    for record in records:
        subject_records[record.subject_key].append(record)  # type: ignore

    for subject_key, s_records in subject_records.items():
        # sort by date_created to simulate longitudinal timeline
        s_records.sort(key=lambda r: r.date_created if r.date_created else r.date_updated)  # type: ignore

        context = SubjectContext(subject_key)

        # We will collect ADSL components iteratively, emitting one ADSL record per subject at the end
        adsl_payload: dict[str, Any] = {"subjectKey": subject_key}
        has_adsl_rules = False

        for record in s_records:
            top_level_payload = {
                **record.model_dump(by_alias=False),
                **record.model_dump(by_alias=True),
            }

            for domain, by_form in grouped_mappings.items():
                rules = by_form.get(record.form_key)  # type: ignore
                if not rules:
                    continue

                payload: dict[str, Any] = {}
                for rule in rules:
                    # 1. Source value extraction
                    if rule.source_variable_name:
                        value = _extract_rule_value_from_payload(record, rule, top_level_payload)
                    else:
                        value = None

                    if _is_missing_value(value) and rule.fallback_value is not None:
                        value = rule.fallback_value

                    # 2. Business Logic Execution
                    if rule.business_logic:
                        derived = _evaluate_business_logic(
                            rule.business_logic, record, payload, context, value
                        )
                        if derived is not None:
                            value = derived

                    payload[rule.target_field] = value

                    # Update ADSL payload if domain is ADSL
                    if domain == "ADSL":
                        has_adsl_rules = True
                        if value is not None:
                            adsl_payload[rule.target_field] = value

                    # Update state context for cross-dataset dependency
                    context.state[f"{domain}.{rule.target_field}"] = value

                    # Update baseline if marked
                    if getattr(rule, "is_baseline", False) and value is not None:
                        baseline_key = f"{domain}.{rule.target_field}"
                        if baseline_key not in context.baseline:
                            context.baseline[baseline_key] = value

                # ADSL is subject-level, we accumulate and create it at the end
                if domain == "ADSL":
                    continue

                model_type = _DOMAIN_MODEL_MAP[domain]
                try:
                    model_instance = model_type(**payload)
                except ValidationError as exc:
                    result.validation_errors.append(
                        {
                            "recordId": cast(str, record.record_id),  # type: ignore
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
                elif domain == "DD":
                    result.device_deficiencies.append(model_instance)
                elif domain == "ADAE":
                    result.adae_records.append(model_instance)
                elif domain == "ADLB":
                    result.adlb_records.append(model_instance)

        if has_adsl_rules:
            try:
                adsl_instance = SubjectLevelAnalysis(**adsl_payload)
                result.adsl_records.append(adsl_instance)
            except ValidationError as exc:
                result.validation_errors.append(
                    {
                        "recordId": "ADSL",
                        "formKey": "N/A",
                        "domain": "ADSL",
                        "payload": adsl_payload,
                        "errors": exc.errors(),
                    }
                )

    return result


__all__ = ["ExtractionResult", "extract_canonical_records"]
