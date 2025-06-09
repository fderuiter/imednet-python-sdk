"""Data quality and integrity checking utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple

from ..models import Record

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..sdk import ImednetSDK


class DataQualityWorkflow:
    """Workflow helpers for validating data quality across a study."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    # Internal helpers
    def _get_required_variables(self, study_key: str) -> List[str]:
        variables = self._sdk.variables.list(study_key)
        return [getattr(v, "variable_name", "") for v in variables if getattr(v, "required", False)]

    def _get_coding_values(self, study_key: str) -> Dict[str, set[str]]:
        codings = self._sdk.codings.list(study_key)
        mapping: Dict[str, set[str]] = {}
        for c in codings:
            var = getattr(c, "variable", "")
            val = str(getattr(c, "value", ""))
            mapping.setdefault(var, set()).add(val)
        return mapping

    def check_missing_required(self, study_key: str) -> List[Record]:
        """Return records missing values for required variables."""
        required = self._get_required_variables(study_key)
        if not required:
            return []
        records = self._sdk.records.list(study_key)
        missing: List[Record] = []
        for rec in records:
            data = rec.record_data or {}
            for var in required:
                if not data.get(var):
                    missing.append(rec)
                    break
        return missing

    def check_coding_consistency(self, study_key: str) -> List[Tuple[Record, str]]:
        """Return records containing values not present in the codings table."""
        allowed = self._get_coding_values(study_key)
        if not allowed:
            return []
        records = self._sdk.records.list(study_key)
        mismatches: List[Tuple[Record, str]] = []
        for rec in records:
            for var, value in (rec.record_data or {}).items():
                if var in allowed and str(value) not in allowed[var]:
                    mismatches.append((rec, f"{var}: {value} not coded"))
        return mismatches

    def check_invalid_data_types(self, study_key: str) -> List[Tuple[Record, str]]:
        """Simple type checking of record values against variable definitions."""
        variables = self._sdk.variables.list(study_key)
        type_map = {
            getattr(v, "variable_name", ""): getattr(v, "variable_type", "").lower()
            for v in variables
        }
        records = self._sdk.records.list(study_key)
        issues: List[Tuple[Record, str]] = []
        for rec in records:
            for var, value in (rec.record_data or {}).items():
                expected = type_map.get(var)
                if not expected or value is None:
                    continue
                if "int" in expected and not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        issues.append((rec, f"{var} expected integer"))
                elif "float" in expected and not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        issues.append((rec, f"{var} expected float"))
        return issues
