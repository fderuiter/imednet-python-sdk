from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from imednet.models.forms import Form
from imednet.models.records import Record
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaCache

from .cached_loader import CachedRecordsLoader

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK

_SCHEMA_TYPE_MAP = {
    "bool": "boolean",
    "boolean": "boolean",
    "checkbox": "boolean",
    "date": "date",
    "datetime": "date",
    "decimal": "numeric",
    "float": "numeric",
    "int": "numeric",
    "integer": "numeric",
    "number": "numeric",
}


class FieldProfile(BaseModel):
    """Summary statistics for a single form field."""

    variable_name: str
    label: str
    population_rate: float
    inferred_type: str
    unique_count: int = 0
    unique_values: list[str] = Field(default_factory=list)


class FormProfile(BaseModel):
    """Summary statistics for a single form."""

    form_key: str
    form_name: str
    record_count: int
    fields: dict[str, FieldProfile] = Field(default_factory=dict)


class SchemaProfiler:
    """Profile form and record-data population across cached records."""

    def __init__(self, sdk: "ImednetSDK", loader: CachedRecordsLoader | None = None) -> None:
        self._sdk = sdk
        self._loader = loader

    def profile_records(
        self,
        study_key: str,
        *,
        records: list[Record] | None = None,
    ) -> dict[str, FormProfile]:
        """Return per-form field profiling statistics for ``study_key``."""
        forms = self._sdk.forms.list(study_key=study_key)
        variables = self._sdk.variables.list(study_key=study_key)
        schema = SchemaCache()
        schema.populate(variables)
        form_names = {form.form_key: form.form_name for form in forms}
        records = records if records is not None else self._load_records(study_key)

        grouped_records: dict[str, list[Record]] = defaultdict(list)
        for record in records:
            form_key = record.form_key or schema.form_key_from_id(record.form_id) or str(record.form_id)
            grouped_records[form_key].append(record)

        profiles: dict[str, FormProfile] = {}
        for form_key, form_records in grouped_records.items():
            schema_variables = schema.variables_for_form(form_key)
            field_names = set(schema_variables)
            for record in form_records:
                if isinstance(record.record_data, dict):
                    field_names.update(record.record_data)

            fields = {
                field_name: self._build_field_profile(
                    field_name=field_name,
                    records=form_records,
                    variable=schema_variables.get(field_name),
                )
                for field_name in sorted(field_names)
            }
            profiles[form_key] = FormProfile(
                form_key=form_key,
                form_name=form_names.get(form_key, form_key),
                record_count=len(form_records),
                fields=fields,
            )
        return profiles

    def _load_records(self, study_key: str) -> list[Record]:
        if self._loader is None:
            self._loader = CachedRecordsLoader(self._sdk)
        return self._loader.load_records(study_key)

    def _build_field_profile(
        self,
        *,
        field_name: str,
        records: list[Record],
        variable: Variable | None,
    ) -> FieldProfile:
        populated_values: list[Any] = []
        sample_values: list[str] = []
        distinct_values: set[str] = set()

        for record in records:
            value = record.record_data.get(field_name) if isinstance(record.record_data, dict) else None
            if not _is_populated(value):
                continue
            populated_values.append(value)
            rendered_value = _render_value(value)
            if rendered_value not in distinct_values and len(sample_values) < 10:
                sample_values.append(rendered_value)
            distinct_values.add(rendered_value)

        inferred_type = _infer_type(populated_values, variable)
        population_rate = 0.0
        if records:
            population_rate = round((len(populated_values) / len(records)) * 100, 2)

        label = field_name
        if variable is not None and variable.label:
            label = variable.label

        return FieldProfile(
            variable_name=field_name,
            label=label,
            population_rate=population_rate,
            inferred_type=inferred_type,
            unique_count=len(distinct_values),
            unique_values=sample_values,
        )


def _is_populated(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, dict)):
        return len(value) > 0
    return True


def _render_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def _infer_type(values: list[Any], variable: Variable | None) -> str:
    if values:
        if all(_is_boolean_value(value) for value in values):
            return "boolean"
        if all(_is_numeric_value(value) for value in values):
            return "numeric"
        if all(_is_date_value(value) for value in values):
            return "date"
        return "string"

    if variable is None:
        return "string"
    return _SCHEMA_TYPE_MAP.get(variable.variable_type.lower(), "string")


def _is_boolean_value(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"true", "false", "yes", "no"}
    return False


def _is_numeric_value(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value.strip())
        except ValueError:
            return False
        return True
    return False


def _is_date_value(value: Any) -> bool:
    if isinstance(value, (date, datetime)):
        return True
    if not isinstance(value, str):
        return False

    normalised = value.strip()
    if not normalised:
        return False
    try:
        datetime.fromisoformat(normalised.replace("Z", "+00:00"))
        return True
    except ValueError:
        try:
            date.fromisoformat(normalised)
        except ValueError:
            return False
        return True
