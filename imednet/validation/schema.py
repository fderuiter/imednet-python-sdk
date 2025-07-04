"""Utilities for caching form variable metadata and validating record data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

from ..core.exceptions import UnknownVariableTypeError, ValidationError
from ..endpoints.forms import FormsEndpoint
from ..endpoints.variables import VariablesEndpoint
from ..models.variables import Variable
from ._base import _ValidatorMixin


def _validate_int(value: Any) -> None:
    if not isinstance(value, int):
        raise ValidationError("Value must be an integer")


def _validate_float(value: Any) -> None:
    if not isinstance(value, (int, float)):
        raise ValidationError("Value must be numeric")


def _validate_bool(value: Any) -> None:
    if not isinstance(value, bool):
        raise ValidationError("Value must be boolean")


def _validate_text(value: Any) -> None:
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")


_TYPE_VALIDATORS: dict[str, Callable[[Any], None]] = {
    "int": _validate_int,
    "integer": _validate_int,
    "number": _validate_int,
    "float": _validate_float,
    "decimal": _validate_float,
    "bool": _validate_bool,
    "boolean": _validate_bool,
    "text": _validate_text,
    "string": _validate_text,
}

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class SchemaCache:
    """Cache of variables by form key."""

    def __init__(self) -> None:
        self._form_variables: Dict[str, Dict[str, Variable]] = {}
        self._form_id_to_key: Dict[int, str] = {}

    def refresh(
        self,
        forms: FormsEndpoint,
        variables: VariablesEndpoint,
        study_key: Optional[str] = None,
    ) -> None:
        """Reload variable metadata for the given study."""
        self._form_variables.clear()
        self._form_id_to_key.clear()
        for form in forms.list(study_key=study_key):
            self._form_id_to_key[form.form_id] = form.form_key
            vars_for_form = variables.list(study_key=study_key, formId=form.form_id)
            self._form_variables[form.form_key] = {v.variable_name: v for v in vars_for_form}

    def variables_for_form(self, form_key: str) -> Dict[str, Variable]:
        return self._form_variables.get(form_key, {})

    def form_key_from_id(self, form_id: int) -> Optional[str]:
        return self._form_id_to_key.get(form_id)


def _check_type(var_type: str, value: Any) -> None:
    if value is None:
        return
    try:
        validator = _TYPE_VALIDATORS[var_type.lower()]
    except KeyError:
        raise UnknownVariableTypeError(var_type)
    validator(value)


def validate_record_data(
    schema: SchemaCache,
    form_key: str,
    data: Dict[str, Any],
) -> None:
    """Validate record data against cached variable metadata."""
    variables = schema.variables_for_form(form_key)
    if not variables:
        return
    unknown = [k for k in data if k not in variables]
    if unknown:
        raise ValidationError(f"Unknown variables for form {form_key}: {', '.join(unknown)}")
    missing_required = [
        name
        for name, var in variables.items()
        if getattr(var, "required", False) and name not in data
    ]
    if missing_required:
        raise ValidationError(
            f"Missing required variables for form {form_key}: {', '.join(missing_required)}"
        )
    for name, value in data.items():
        _check_type(variables[name].variable_type, value)


class SchemaValidator(_ValidatorMixin):
    """Validate record payloads using variable metadata from the API."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk
        self.schema = SchemaCache()

    def refresh(self, study_key: str) -> None:
        """Load variable definitions for ``study_key`` using :meth:`sdk.variables.list`."""
        self.schema._form_variables.clear()
        self.schema._form_id_to_key.clear()
        variables = self._sdk.variables.list(study_key=study_key, refresh=True)
        for var in variables:
            self.schema._form_id_to_key[var.form_id] = var.form_key
            self.schema._form_variables.setdefault(var.form_key, {})[var.variable_name] = var

    def validate_record(self, study_key: str, record: Dict[str, Any]) -> None:
        form_key = self._resolve_form_key(record)
        if form_key and not self.schema.variables_for_form(form_key):
            self.refresh(study_key)
        self._validate_cached(form_key, record.get("data", {}))

    def validate_batch(self, study_key: str, records: list[Dict[str, Any]]) -> None:
        for rec in records:
            self.validate_record(study_key, rec)
