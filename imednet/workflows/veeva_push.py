"""Workflow for pushing data to Veeva Vault."""

from __future__ import annotations

from typing import Any, Iterable, List, MutableMapping

from ..veeva import VeevaVaultClient, validate_record_for_upsert


class VeevaPushWorkflow:
    """Push iMednet record data to Veeva Vault objects."""

    def __init__(self, client: VeevaVaultClient) -> None:
        self._client = client

    def push_record(
        self,
        object_name: str,
        record: MutableMapping[str, Any],
        *,
        object_type: str | None = None,
    ) -> MutableMapping[str, Any]:
        """Validate and upsert a single record."""
        validated = validate_record_for_upsert(self._client, object_name, record, object_type)
        return self._client.upsert_object(object_name, validated)

    def push_records(
        self,
        object_name: str,
        records: Iterable[MutableMapping[str, Any]],
        *,
        object_type: str | None = None,
    ) -> List[MutableMapping[str, Any]]:
        """Validate and upsert multiple records."""
        results: List[MutableMapping[str, Any]] = []
        for record in records:
            results.append(self.push_record(object_name, record, object_type=object_type))
        return results
