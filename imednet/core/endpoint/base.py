"""
Base endpoint mix-in for all API resource endpoints.
"""

from typing import Any, Dict, Optional
from urllib.parse import quote

from imednet.core.context import Context
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol


class BaseEndpoint:
    """
    Shared base for endpoint wrappers.

    Handles context injection and filtering.
    """

    BASE_PATH = ""

    PATH: str  # to be set in subclasses

    def __init__(
        self,
        client: RequestorProtocol,
        ctx: Context,
        async_client: AsyncRequestorProtocol | None = None,
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
        Hook to modify filters before they are processed.

        Subclasses (or mixins) should override this to inject default values.
        """
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Return an API path joined with :data:`BASE_PATH`."""
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
