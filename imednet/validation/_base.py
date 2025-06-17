from __future__ import annotations

from typing import Any, Dict, Optional


class _ValidatorMixin:
    """Shared logic for schema validators."""

    schema: Any

    def _resolve_form_key(self, record: Dict[str, Any]) -> Optional[str]:
        return record.get("formKey") or self.schema.form_key_from_id(record.get("formId", 0))

    def _validate_cached(self, form_key: Optional[str], data: Dict[str, Any]) -> None:
        if form_key:
            from .schema import validate_record_data

            validate_record_data(self.schema, form_key, data)
