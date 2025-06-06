"""
Base endpoint mix-in for all API resource endpoints.
"""

from typing import Any, Dict, Generic, TypeVar

from imednet.core.context import Context

TClient = TypeVar("TClient")


class BaseEndpoint(Generic[TClient]):
    """
    Shared base for endpoint wrappers.

    Handles context injection and filtering.
    """

    path: str  # to be set in subclasses

    def __init__(self, client: TClient, ctx: Context, default_page_size: int = 100) -> None:
        self._client = client
        self._ctx = ctx
        self._default_page_size = default_page_size

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        # inject default studyKey if missing
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters

    def _build_path(self, *args: Any) -> str:
        # join path segments after base path
        segments = [self.path.strip("/")] + [str(a).strip("/") for a in args]
        return "/" + "/".join(segments)
