from __future__ import annotations

from typing import Any, Dict, Optional


class _ValidatorMixin:
    """A mixin that provides shared logic for schema validators."""

    schema: Any

    def _resolve_form_key(self, record: Dict[str, Any]) -> Optional[str]:
        """Resolve the form key from a record, falling back to the form ID.

        Args:
            record: The record dictionary.

        Returns:
            The form key, or `None` if it could not be resolved.
        """
        return record.get("formKey") or self.schema.form_key_from_id(record.get("formId", 0))

    def _validate_cached(self, form_key: Optional[str], data: Dict[str, Any]) -> None:
        """Validate a record's data against the cached schema for a form.

        Args:
            form_key: The key of the form to validate against.
            data: The record data dictionary.
        """
        if form_key:
            from .cache import validate_record_data

            validate_record_data(self.schema, form_key, data)
