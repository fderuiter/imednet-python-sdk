"""Asynchronous schema validation utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..endpoints.forms import FormsEndpoint
from ..endpoints.variables import VariablesEndpoint
from ..models.variables import Variable

if TYPE_CHECKING:
    from ..sdk import AsyncImednetSDK
from ._base import _ValidatorMixin


class AsyncSchemaCache:
    """Cache of variables by form key with asynchronous refresh."""

    def __init__(self) -> None:
        self._form_variables: Dict[str, Dict[str, Variable]] = {}
        self._form_id_to_key: Dict[int, str] = {}

    async def refresh(
        self,
        forms: FormsEndpoint,
        variables: VariablesEndpoint,
        study_key: Optional[str] = None,
    ) -> None:
        self._form_variables.clear()
        self._form_id_to_key.clear()
        for form in await forms.async_list(study_key=study_key):
            self._form_id_to_key[form.form_id] = form.form_key
            vars_for_form = await variables.async_list(study_key=study_key, formId=form.form_id)
            self._form_variables[form.form_key] = {v.variable_name: v for v in vars_for_form}

    def variables_for_form(self, form_key: str) -> Dict[str, Variable]:
        return self._form_variables.get(form_key, {})

    def form_key_from_id(self, form_id: int) -> Optional[str]:
        return self._form_id_to_key.get(form_id)


class AsyncSchemaValidator(_ValidatorMixin):
    """Validate records asynchronously using variable metadata."""

    def __init__(self, sdk: "AsyncImednetSDK") -> None:
        self._sdk = sdk
        self.schema = AsyncSchemaCache()

    async def refresh(self, study_key: str) -> None:
        self.schema._form_variables.clear()
        self.schema._form_id_to_key.clear()
        variables = await self._sdk.variables.async_list(study_key=study_key, refresh=True)
        for var in variables:
            self.schema._form_id_to_key[var.form_id] = var.form_key
            self.schema._form_variables.setdefault(var.form_key, {})[var.variable_name] = var

    async def validate_record(self, study_key: str, record: Dict[str, Any]) -> None:
        form_key = self._resolve_form_key(record)
        if form_key and not self.schema.variables_for_form(form_key):
            await self.refresh(study_key)
        self._validate_cached(form_key, record.get("data", {}))

    async def validate_batch(self, study_key: str, records: list[Dict[str, Any]]) -> None:
        for rec in records:
            await self.validate_record(study_key, rec)
