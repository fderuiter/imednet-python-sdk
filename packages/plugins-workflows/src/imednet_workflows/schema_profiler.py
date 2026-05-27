from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

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
        records: Iterable[Record] | None = None,
    ) -> dict[str, FormProfile]:
        """Return per-form field profiling statistics for ``study_key``."""
        forms = self._sdk.forms.list(study_key=study_key)
        variables = self._sdk.variables.list(study_key=study_key)
        schema = SchemaCache()
        schema.populate(variables)
        form_names = {form.form_key: form.form_name for form in forms}
        records_iterable = records if records is not None else self._iter_records(study_key)

        form_accumulators: dict[str, _FormAccumulator] = {}
        for record in records_iterable:
            form_key = (
                record.form_key or schema.form_key_from_id(record.form_id) or str(record.form_id)
            )
            accumulator = form_accumulators.setdefault(form_key, _FormAccumulator())
            accumulator.record_count += 1

            if not isinstance(record.record_data, dict):
                continue
            for field_name, value in record.record_data.items():
                field_accumulator = accumulator.fields.setdefault(field_name, _FieldAccumulator())
                field_accumulator.observe(value)

        profiles: dict[str, FormProfile] = {}
        for form_key, accumulator in form_accumulators.items():
            schema_variables = schema.variables_for_form(form_key)
            field_names = sorted(set(schema_variables).union(accumulator.fields))

            fields = {
                field_name: self._build_field_profile(
                    field_name=field_name,
                    record_count=accumulator.record_count,
                    accumulator=accumulator.fields.get(field_name, _FieldAccumulator()),
                    variable=schema_variables.get(field_name),
                )
                for field_name in field_names
            }
            profiles[form_key] = FormProfile(
                form_key=form_key,
                form_name=form_names.get(form_key, form_key),
                record_count=accumulator.record_count,
                fields=fields,
            )
        return profiles

    def _iter_records(self, study_key: str) -> Iterable[Record]:
        if self._loader is None:
            self._loader = CachedRecordsLoader(self._sdk)
        sync_method = getattr(self._loader, "sync_records", None)
        # Check class-level iterator presence to avoid dynamic mock attributes
        # being treated as real chunked iterators.
        iter_method = getattr(type(self._loader), "iter_cached_records", None)
        if callable(iter_method):
            if callable(sync_method):
                sync_method(study_key)
            else:
                self._loader.load_records(study_key)
            return self._loader.iter_cached_records(study_key)
        return self._loader.load_records(study_key)

    def _build_field_profile(
        self,
        *,
        field_name: str,
        record_count: int,
        accumulator: "_FieldAccumulator",
        variable: Variable | None,
    ) -> FieldProfile:
        inferred_type = accumulator.inferred_type(variable)
        population_rate = 0.0
        if record_count:
            population_rate = round((accumulator.populated_count / record_count) * 100, 2)

        label = field_name
        if variable is not None and variable.label:
            label = variable.label

        return FieldProfile(
            variable_name=field_name,
            label=label,
            population_rate=population_rate,
            inferred_type=inferred_type,
            unique_count=accumulator.unique_count,
            unique_values=accumulator.sample_values,
        )


@dataclass
class _FormAccumulator:
    record_count: int = 0
    fields: dict[str, "_FieldAccumulator"] = field(default_factory=dict)


@dataclass
class _FieldAccumulator:
    populated_count: int = 0
    unique_values: set[str] = field(default_factory=set)
    sample_values: list[str] = field(default_factory=list)
    all_boolean: bool = True
    all_numeric: bool = True
    all_date: bool = True

    @property
    def unique_count(self) -> int:
        return len(self.unique_values)

    def observe(self, value: Any) -> None:
        if not _is_populated(value):
            return

        self.populated_count += 1
        rendered_value = _render_value(value)
        if rendered_value not in self.unique_values and len(self.sample_values) < 10:
            self.sample_values.append(rendered_value)
        self.unique_values.add(rendered_value)

        self.all_boolean = self.all_boolean and _is_boolean_value(value)
        self.all_numeric = self.all_numeric and _is_numeric_value(value)
        self.all_date = self.all_date and _is_date_value(value)

    def inferred_type(self, variable: Variable | None) -> str:
        if self.populated_count > 0:
            if self.all_boolean:
                return "boolean"
            if self.all_numeric:
                return "numeric"
            if self.all_date:
                return "date"
            return "string"

        if variable is None:
            return "string"
        return _SCHEMA_TYPE_MAP.get(variable.variable_type.lower(), "string")


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
