"""
Base endpoint mix-in for all API resource endpoints.
"""

from typing import Any, Dict, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context


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
        async_client: AsyncClient | None = None,
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
        # inject default studyKey if missing
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Return an API path joined with :data:`BASE_PATH`."""

        parts = [self.BASE_PATH.strip("/")]
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                parts.append(text)
        return "/" + "/".join(parts)

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _fallback_from_list(self, study_key: str, item_id: Any, attr: str):
        """Return an item from ``list`` when direct ``get`` fails."""
        for item in self.list(study_key):  # type: ignore[attr-defined]
            if str(getattr(item, attr)) == str(item_id):
                return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    async def _async_fallback_from_list(self, study_key: str, item_id: Any, attr: str):
        for item in await self.async_list(study_key):  # type: ignore[attr-defined]
            if str(getattr(item, attr)) == str(item_id):
                return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    def _require_async_client(self) -> AsyncClient:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client
