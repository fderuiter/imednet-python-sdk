"""EDC-specific endpoint mixin."""

from __future__ import annotations

from typing import Any, Dict, Protocol, cast
from urllib.parse import quote

from imednet.core.context import Context


class ContextProtocol(Protocol):
    """Protocol ensuring context availability."""

    _ctx: Context


class EdcEndpointMixin:
    """
    Mixin for EDC-specific endpoint logic.

    Provides implementation for ``_auto_filter`` (studyKey injection)
    and ``_build_path`` (prepending EDC base path).

    Expects the consuming class to have a ``_ctx`` attribute of type :class:`Context`.
    """

    BASE_PATH = "/api/v1/edc/studies"

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing.

        Args:
            filters: Dictionary of query filters.

        Returns:
            Updated filters dictionary with studyKey injected if applicable.
        """
        # Cast self to ensure type checker knows about _ctx
        instance = cast(ContextProtocol, self)

        if "studyKey" not in filters and instance._ctx.default_study_key:
            filters["studyKey"] = instance._ctx.default_study_key
        return filters

    def _build_path(self, *segments: Any) -> str:
        """
        Return an API path joined with :data:`BASE_PATH`.

        Args:
            *segments: Path segments to append.

        Returns:
            Full URL path string.
        """
        parts = [self.BASE_PATH.strip("/")]
        for seg in segments:
            text = str(seg).strip("/")
            if text:
                # Encode path segments to prevent traversal and injection
                parts.append(quote(text, safe=""))
        return "/" + "/".join(parts)
