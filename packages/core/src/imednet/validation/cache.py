from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Dict, Generic, Iterable, Optional, Tuple, TypeVar

from imednet.errors import UnknownVariableTypeError, ValidationError

from ..models.variables import Variable
from ._base import _ValidatorMixin

if TYPE_CHECKING:
    from ..endpoints.forms import FormsEndpoint
    from ..endpoints.variables import VariablesEndpoint
    from ..sdk import AsyncImednetSDK, ImednetSDK

_TClient = TypeVar("_TClient")


class BaseSchemaCache(Generic[_TClient]):
    """Cache of variables by form key with optional async refresh."""

    def __init__(self, is_async: bool) -> None:
        self._is_async = is_async
        self._form_variables: Dict[str, Dict[str, Variable]] = {}
        self._form_id_to_key: Dict[int, str] = {}

    def populate(self, variables: Iterable[Variable]) -> None:
        """Populate the cache with the given variables."""
        self._form_variables.clear()
        self._form_id_to_key.clear()
        for var in variables:
            self._form_id_to_key[var.form_id] = var.form_key
            self._form_variables.setdefault(var.form_key, {})[var.variable_name] = var

    async def _refresh_async(
        self,
        forms: FormsEndpoint,
        variables: VariablesEndpoint,
        study_key: Optional[str] = None,
    ) -> None:
        vars_list = await variables.async_list(study_key=study_key, refresh=True)
        self.populate(vars_list)

    def _refresh_sync(
        self,
        forms: FormsEndpoint,
        variables: VariablesEndpoint,
        study_key: Optional[str] = None,
    ) -> None:
        vars_list = variables.list(study_key=study_key, refresh=True)
        self.populate(vars_list)

    def refresh(
        self,
        forms: FormsEndpoint,
        variables: VariablesEndpoint,
        study_key: Optional[str] = None,
    ) -> Any:
        if self._is_async:
            return self._refresh_async(forms, variables, study_key)
        return self._refresh_sync(forms, variables, study_key)

    def variables_for_form(self, form_key: str) -> Dict[str, Variable]:
        return self._form_variables.get(form_key, {})

    def form_key_from_id(self, form_id: int) -> Optional[str]:
        return self._form_id_to_key.get(form_id)

    @property
    def forms(self) -> Dict[str, Dict[str, Variable]]:
        """Return cached variables grouped by form key."""
        return self._form_variables


class SchemaCache(BaseSchemaCache["ImednetSDK"]):
    def __init__(self) -> None:
        super().__init__(is_async=False)


class AsyncSchemaCache(BaseSchemaCache["AsyncImednetSDK"]):
    def __init__(self) -> None:
        super().__init__(is_async=True)


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


_TYPE_VALIDATORS: Dict[str, Callable[[Any], None]] = {
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

# Bolt Optimization: Expand validators to include common casings
# to avoid .lower() allocation in hot paths.
for key, validator in list(_TYPE_VALIDATORS.items()):
    _TYPE_VALIDATORS[key.capitalize()] = validator
    _TYPE_VALIDATORS[key.upper()] = validator


def _check_type(var_type: str, value: Any) -> None:
    if value is None:
        return

    # Bolt Optimization: Try direct lookup first to avoid string manipulation
    try:
        validator = _TYPE_VALIDATORS[var_type]
    except KeyError:
        try:
            validator = _TYPE_VALIDATORS[var_type.lower()]
        except KeyError:
            raise UnknownVariableTypeError(var_type) from None

    validator(value)


def validate_record_data(
    schema: BaseSchemaCache[Any],
    form_key: str,
    data: Dict[str, Any],
) -> None:
    """Validate ``data`` for ``form_key`` using the provided schema cache.

    Raises:
        ValidationError: If the form key is not present in the schema or the data
            fails validation checks.
    """

    variables = schema.variables_for_form(form_key)
    if not variables:
        # The cache has no variables for the given form key, so treat it as an
        # unknown form and fail fast.
        raise ValidationError(f"Unknown form {form_key}")
    unknown = [k for k in data if k not in variables]
    if unknown:
        raise ValidationError(f"Unknown variables for form {form_key}: {', '.join(unknown)}")
    # Bolt Optimization: Removed dead code iterating over all variables for 'required' check.
    # The Variable model does not have a 'required' field, so this loop was O(N) for no-op.
    for name, value in data.items():
        _check_type(variables[name].variable_type, value)


def validate_record_entry(
    schema: BaseSchemaCache[Any],
    record: Dict[str, Any],
) -> None:
    """
    Validate a single record entry against the schema.

    Resolves the form key from "formKey", "form_key", "formId", or "form_id".

    Args:
        schema: The schema cache to use for validation.
        record: The record data dictionary.

    Raises:
        ValidationError: If the form key is not present in the schema or the data
            fails validation checks.
    """
    fk = record.get("formKey") or record.get("form_key")
    if not fk:
        fid = record.get("formId") or record.get("form_id") or 0
        fk = schema.form_key_from_id(fid)
    if fk:
        validate_record_data(schema, fk, record.get("data", {}))


class BaseSchemaValidator(_ValidatorMixin, Generic[_TClient]):
    """Base validator sharing logic between sync and async implementations."""

    schema: BaseSchemaCache[_TClient]

    def _refresh_common(self, variables: Iterable[Variable]) -> None:
        self.schema.populate(variables)

    def _needs_refresh(self, record: Dict[str, Any]) -> Tuple[Optional[str], bool]:
        """
        Determine if the schema cache needs refreshing for the given record.

        Returns:
            A tuple of (form_key, needs_refresh).
        """
        form_key = self._resolve_form_key(record)
        needs_refresh = bool(form_key and not self.schema.variables_for_form(form_key))
        return form_key, needs_refresh


class SchemaValidator(BaseSchemaValidator["ImednetSDK"]):
    """Validate record payloads using variable metadata from the API (Synchronous)."""

    def __new__(cls, sdk: "ImednetSDK", *args: Any, **kwargs: Any) -> Any:
        if kwargs.get("is_async") or (args and args[0] is True):
            import warnings

            warnings.warn(
                "Passing `is_async=True` to SchemaValidator is deprecated. "
                "Use `AsyncSchemaValidator` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return AsyncSchemaValidator(sdk)  # type: ignore[arg-type]
        return super().__new__(cls)

    def __init__(self, sdk: ImednetSDK, *, is_async: bool = False) -> None:
        """Initialize the synchronous schema validator."""
        self._sdk = sdk
        self.schema = SchemaCache()

    def refresh(self, study_key: str) -> None:
        """Populate the schema cache for ``study_key`` from the Variables endpoint.

        This method never raises :class:`~imednet.errors.ValidationError`;
        any API errors bubble up as :class:`~imednet.errors.ApiError`.
        """
        variables = self._sdk.variables.list(study_key=study_key, refresh=True)
        self._refresh_common(variables)

    def validate_record(self, study_key: str, record: Dict[str, Any]) -> None:
        """Validate a single record payload."""
        form_key, needs_refresh = self._needs_refresh(record)
        if needs_refresh:
            self.refresh(study_key)
        self._validate_cached(form_key, record.get("data", {}))

    def validate_batch(self, study_key: str, records: list[Dict[str, Any]]) -> None:
        """Validate a batch of record payloads."""
        for rec in records:
            self.validate_record(study_key, rec)


class AsyncSchemaValidator(BaseSchemaValidator["AsyncImednetSDK"]):
    """Validate record payloads using variable metadata from the API (Asynchronous)."""

    def __init__(self, sdk: AsyncImednetSDK) -> None:
        """Initialize the asynchronous schema validator."""
        self._sdk = sdk
        self.schema = AsyncSchemaCache()

    async def refresh(self, study_key: str) -> None:
        """Populate the schema cache for ``study_key`` from the Variables endpoint.

        This method never raises :class:`~imednet.errors.ValidationError`;
        any API errors bubble up as :class:`~imednet.errors.ApiError`.
        """
        variables = await self._sdk.variables.async_list(study_key=study_key, refresh=True)
        self._refresh_common(variables)

    async def validate_record(self, study_key: str, record: Dict[str, Any]) -> None:
        """Validate a single record payload asynchronously."""
        form_key, needs_refresh = self._needs_refresh(record)
        if needs_refresh:
            await self.refresh(study_key)
        self._validate_cached(form_key, record.get("data", {}))

    async def validate_batch(self, study_key: str, records: list[Dict[str, Any]]) -> None:
        """Validate a batch of record payloads asynchronously."""
        for rec in records:
            await self.validate_record(study_key, rec)
