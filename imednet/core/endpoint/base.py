"""
Base endpoint mix-in for all API resource endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, TypeVar
from urllib.parse import quote

from imednet.core.context import Context
from imednet.core.endpoint.abc import EndpointABC
from imednet.core.endpoint.edc_mixin import EdcEndpointMixin
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class GenericEndpoint(EndpointABC[T]):
    """
    Generic base for endpoint wrappers.

    Handles context injection and basic path building.
    Does NOT include EDC-specific logic.
    """

    BASE_PATH = ""

    def __init__(
        self,
        client: RequestorProtocol,
        ctx: Context,
        async_client: AsyncRequestorProtocol | None = None,
    ) -> None:
        self._client = client
        self._async_client = async_client
        self._ctx = ctx

        # Initialize cache if configured
        cache_name = self._cache_name
        if cache_name:
            if self.requires_study_key:
                setattr(self, cache_name, {})
            else:
                setattr(self, cache_name, None)

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Pass-through for filters in generic endpoints."""
        return filters

    def _build_path(self, *segments: Any) -> str:
        """
        Return an API path joined with :data:`BASE_PATH`.

        Args:
            *segments: URL path segments to append.

        Returns:
            The full API path string.
        """
        base = self.BASE_PATH.strip("/")
        parts = [base] if base else []
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client


class BaseEndpoint(EdcEndpointMixin, GenericEndpoint[T]):
    """
    Shared base for endpoint wrappers (Legacy).

    Includes EDC-specific logic for backward compatibility.
    New endpoints should use GenericEndpoint or explicit Edc* mixins.
    """

    pass
