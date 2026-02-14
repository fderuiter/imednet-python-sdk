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


class BaseEndpoint(EndpointABC[T]):
    """
    Shared base for endpoint wrappers.

    Handles context injection and filtering.
    """

    BASE_PATH: str = ""

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
        """
        Apply automatic filters.

        Override in subclasses or mixins to inject default filters (e.g., studyKey).
        """
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Return an API path joined with :data:`BASE_PATH`."""

        parts = [self.BASE_PATH.strip("/")]
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))

        # Ensure the path starts with / but doesn't have double //
        path = "/" + "/".join(p for p in parts if p)
        return path if path.startswith("/") else "/" + path

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """Return the configured async client or raise if missing."""
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client
