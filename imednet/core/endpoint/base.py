"""
Base endpoint mix-in for all API resource endpoints.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict, Optional, Type
from urllib.parse import quote

from imednet.core.context import Context
from imednet.core.protocols import AsyncRequestorProtocol, RequestorProtocol
from imednet.models.json_base import JsonModel


class BaseEndpoint(ABC):
    """
    Shared base for endpoint wrappers.

    Handles context injection and filtering.
    """

    BASE_PATH: str = "/api/v1/edc/studies"

    # Abstract properties to enforce definition in subclasses
    @property
    @abstractmethod
    def PATH(self) -> str:
        """The relative path for this endpoint."""
        ...

    @property
    @abstractmethod
    def MODEL(self) -> Type[JsonModel]:
        """The model class associated with this endpoint."""
        ...

    requires_study_key: bool = True
    _cache_name: Optional[str] = None

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
        if self._cache_name:
            if self.requires_study_key:
                setattr(self, self._cache_name, {})
            else:
                setattr(self, self._cache_name, None)

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically inject default filters (like studyKey) if missing.

        Args:
            filters: The current dictionary of filters.

        Returns:
            The updated dictionary of filters.
        """
        # inject default studyKey if missing
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters

    def _build_path(self, *segments: Any) -> str:
        """
        Return an API path joined with :data:`BASE_PATH`.

        Args:
            *segments: Path segments to append to the base path.

        Returns:
            The full API path string.
        """
        parts = [self.BASE_PATH.strip("/")]
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)

    def _require_async_client(self) -> AsyncRequestorProtocol:
        """
        Return the configured async client or raise if missing.

        Returns:
            The async client instance.

        Raises:
            RuntimeError: If the async client is not configured.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client
