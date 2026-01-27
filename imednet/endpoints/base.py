"""
Base endpoint mix-in for all API resource endpoints.
"""

from typing import Any, Dict, Iterable, Optional
from urllib.parse import quote

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context


def _find_by_attr(items: Iterable[Any], attr: str, value: Any) -> Optional[Any]:
    """Find an item in an iterable by matching a stringified attribute."""
    target = str(value)
    for item in items:
        if str(getattr(item, attr)) == target:
            return item
    return None


class BaseEndpoint:
    """
    Shared base for endpoint wrappers.

    Handles context injection and filtering.
    """

    BASE_PATH = "/api/v1/edc/studies"

    PATH: str  # to be set in subclasses

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: Optional[AsyncClient] = None,
    ) -> None:
        self._client = client
        self._async_client = async_client
        self._ctx = ctx
        cache_name: Optional[str] = getattr(self, "_cache_name", None)
        if cache_name:
            if getattr(self, "requires_study_key", True):
                setattr(self, cache_name, {})
            else:
                setattr(self, cache_name, None)

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing.

        Returns a new dictionary to ensure immutability of the input.
        """
        filters = filters.copy()
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Return an API path joined with :data:`BASE_PATH`."""

        parts = [self.BASE_PATH.strip("/")]
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _fallback_from_list(self, study_key: str, item_id: Any, attr: str) -> Any:
        """Return an item from ``list`` when direct ``get`` fails."""
        item = _find_by_attr(self.list(study_key), attr, item_id)  # type: ignore[attr-defined]
        if item:
            return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    async def _async_fallback_from_list(self, study_key: str, item_id: Any, attr: str) -> Any:
        items = await self.async_list(study_key)  # type: ignore[attr-defined]
        item = _find_by_attr(items, attr, item_id)
        if item:
            return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    def _require_async_client(self) -> AsyncClient:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client
