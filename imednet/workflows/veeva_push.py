"""Workflow for pushing iMednet records to Veeva Vault."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Mapping, Optional

from ..utils.filters import build_filter_string
from ..veeva import VeevaVaultClient, validate_record_for_upsert

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from ..sdk import ImednetSDK


class VeevaPushWorkflow:
    """Pushes form records from iMednet to Veeva Vault."""

    def __init__(self, sdk: "ImednetSDK", client: VeevaVaultClient) -> None:
        self._sdk = sdk
        self._client = client

    def push_form_records(
        self,
        study_key: str,
        form_key: str,
        object_name: str,
        field_mapping: Mapping[str, str],
        *,
        object_type: str | None = None,
        record_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve records for a form and push them to Vault."""
        if self._client._access_token is None:
            self._client.authenticate()

        filters: Dict[str, Any] = {"form_key": form_key}
        if record_filter:
            filters.update(record_filter)

        filter_str = build_filter_string(filters)
        records = self._sdk.records.list(study_key, filter=filter_str)

        responses: List[Dict[str, Any]] = []
        for rec in records:
            mapped = {field_mapping.get(k, k): v for k, v in rec.record_data.items()}
            valid = validate_record_for_upsert(
                self._client,
                object_name,
                mapped,
                object_type=object_type,
            )
            responses.append(self._client.upsert_object(object_name, valid))
        return responses


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.veeva_push.push_form_records(...)`).
