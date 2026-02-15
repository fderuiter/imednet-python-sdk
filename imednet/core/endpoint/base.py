"""
Base endpoint mix-in for all API resource endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, TypeVar
from urllib.parse import quote

from imednet.core.context import Context
from imednet.core.endpoint.abc import EndpointABC
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class GenericEndpoint(EndpointABC[T]):
    """
    Generic base for endpoint wrappers.

    Handles context injection and basic HTTP client setup.
    Does NOT assume EDC-specific paths or filters.
    """

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

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pass-through filter. Subclasses should override.
        """
        return filters

    def _build_path(self, *segments: Any) -> str:
        """
        Build path by joining segments.
        Does not prepend a base path by default.
        """
        parts: list[str] = []
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)


class BaseEndpoint(GenericEndpoint[T]):
    """
    Legacy base for EDC endpoint wrappers.

    Inherits from GenericEndpoint but enforces EDC-specific logic:
    - Prepend /api/v1/edc/studies
    - Inject studyKey from context

    Deprecated: Prefer using GenericEndpoint combined with EdcEndpointMixin.
    """

    BASE_PATH = "/api/v1/edc/studies"

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
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)
