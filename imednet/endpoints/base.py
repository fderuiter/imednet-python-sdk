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
        """Initializes the BaseEndpoint.

        Args:
            client: The synchronous HTTP client.
            ctx: The SDK context.
            async_client: The asynchronous HTTP client.
        """
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
        """Inject the default study key into the filters if it's not present.

        Args:
            filters: The dictionary of filters.

        Returns:
            The filters dictionary with the default study key added if needed.
        """
        # inject default studyKey if missing
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters

    def _build_path(self, *segments: Any) -> str:
        """Construct an API path from the base path and additional segments.

        Args:
            *segments: The segments to append to the base path.

        Returns:
            The full API path.
        """
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
        """Find an item by its ID by listing all items.

        This method is used as a fallback when a direct `get` by ID is not
        available or fails. It iterates through all items in a study and
        returns the one that matches the given ID.

        Args:
            study_key: The key of the study to search in.
            item_id: The ID of the item to find.
            attr: The attribute name of the item's ID.

        Returns:
            The found item.

        Raises:
            ValueError: If the item is not found.
        """
        for item in self.list(study_key):  # type: ignore[attr-defined]
            if str(getattr(item, attr)) == str(item_id):
                return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    async def _async_fallback_from_list(self, study_key: str, item_id: Any, attr: str):
        """Asynchronously find an item by its ID by listing all items.

        This method is the asynchronous version of `_fallback_from_list`.

        Args:
            study_key: The key of the study to search in.
            item_id: The ID of the item to find.
            attr: The attribute name of the item's ID.

        Returns:
            The found item.

        Raises:
            ValueError: If the item is not found.
        """
        for item in await self.async_list(study_key):  # type: ignore[attr-defined]
            if str(getattr(item, attr)) == str(item_id):
                return item
        raise ValueError(f"{attr} {item_id} not found in study {study_key}")

    def _require_async_client(self) -> AsyncClient:
        """Get the async client, raising an error if it's not configured.

        Returns:
            The asynchronous client.

        Raises:
            RuntimeError: If the async client is not configured.
        """
        if self._async_client is None:
            raise RuntimeError("Async client not configured")
        return self._async_client
