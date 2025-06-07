"""Utilities for managing device inventory in a study."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from ..models.records import Record
from ..utils.filters import build_filter_string

if TYPE_CHECKING:  # pragma: no cover - imported for type checking only
    from ..sdk import ImednetSDK


class InventoryManagementWorkflow:
    """Provide helpers for retrieving device catalog information."""

    def __init__(self, sdk: "ImednetSDK") -> None:
        self._sdk = sdk

    def list_catalog_items(self, study_key: str, **filters: Any) -> List[Record]:
        """Return records with ``recordType`` of ``CATALOG``."""
        filter_dict: dict[str, Any] = {"recordType": "CATALOG"}
        if filters:
            filter_dict.update(filters)
        filter_str = build_filter_string(filter_dict)
        return self._sdk.records.list(study_key, filter=filter_str)
