"""Data quality checking workflows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from ..models import Record

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from ..sdk import ImednetSDK


class DataQualityWorkflow:
    """Provides simple workflows for data quality checks."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    # -----------------------------------------------------
    # helper methods
    # -----------------------------------------------------
    def _get_required_variable_names(self, study_key: str) -> List[str]:
        variables = self._sdk.variables.list(study_key)
        required_vars: List[str] = []
        for var in variables:
            if getattr(var, "required", False) and not getattr(var, "disabled", False):
                required_vars.append(var.variable_name)
        return required_vars

    def _get_coding_map(self, study_key: str) -> Dict[Tuple[int, str], str]:
        codings = self._sdk.codings.list(study_key)
        mapping: Dict[Tuple[int, str], str] = {}
        for c in codings:
            mapping[(c.record_id, c.variable)] = c.value
        return mapping

    # -----------------------------------------------------
    # public checks
    # -----------------------------------------------------
    def check_missing_required(self, study_key: str) -> List[Record]:
        """Return records missing values for required variables."""
        required_vars = self._get_required_variable_names(study_key)
        if not required_vars:
            return []
        records = self._sdk.records.list(study_key)
        missing_records: List[Record] = []
        for rec in records:
            for var in required_vars:
                value = rec.record_data.get(var)
                if value in (None, "", []):
                    missing_records.append(rec)
                    break
        return missing_records

    def check_coding_consistency(self, study_key: str) -> List[Tuple[Record, str]]:
        """Return records with coded values mismatching the codings table."""
        coding_map = self._get_coding_map(study_key)
        if not coding_map:
            return []
        records = self._sdk.records.list(study_key)
        mismatches: List[Tuple[Record, str]] = []
        for rec in records:
            for (record_id, variable), coded_value in coding_map.items():
                if record_id != rec.record_id:
                    continue
                record_value = rec.record_data.get(variable)
                if record_value != coded_value:
                    msg = (
                        f"{variable} value '{record_value}' does not match "
                        f"coded value '{coded_value}'"
                    )
                    mismatches.append((rec, msg))
        return mismatches

    def check_invalid_types(self, study_key: str) -> List[Tuple[Record, str]]:
        """Check for obvious data type issues based on variable_type."""
        variables = self._sdk.variables.list(study_key)
        type_map = {v.variable_name: getattr(v, "variable_type", "").lower() for v in variables}
        records = self._sdk.records.list(study_key)
        issues: List[Tuple[Record, str]] = []
        for rec in records:
            for var, value in rec.record_data.items():
                expected = type_map.get(var, "")
                if expected == "number":
                    if value is not None:
                        try:
                            float(value)
                        except (TypeError, ValueError):
                            issues.append((rec, f"{var} expects numeric value"))
                            break
                elif expected == "date":
                    if value is not None and not isinstance(value, str):
                        issues.append((rec, f"{var} expects date string"))
                        break
        return issues
