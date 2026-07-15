"""Base mixin for schema validation logic."""

from __future__ import annotations

from typing import Any, Dict, Optional  # noqa: UP035


class _ValidatorMixin:
    """Shared logic for schema validators."""

    schema: Any

    def _resolve_form_key(self, record: dict[str, Any]) -> str | None:
        """Resolve the form key from a record payload.

        Args:
            record: The record data dictionary.

        Returns:
            Optional[str]: The resolved form key.
        """
        return record.get("formKey") or self.schema.form_key_from_id(record.get("formId", 0))

    def _validate_cached(self, form_key: str | None, data: dict[str, Any]) -> None:
        """Validate data against a cached form schema.

        Args:
            form_key: The form key to validate against.
            data: The record data to validate.
        """
        if form_key:
            from .cache import validate_record_data

            validate_record_data(self.schema, form_key, data)
