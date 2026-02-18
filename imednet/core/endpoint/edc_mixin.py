"""Mixin for EDC-specific endpoint logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from imednet.core.context import Context


class EdcEndpointMixin:
    """
    Mixin providing EDC-specific logic for endpoints.

    This includes the base path for EDC resources and automatic injection
    of the default study key into filters.
    """

    BASE_PATH = "/api/v1/edc/studies"

    if TYPE_CHECKING:
        _ctx: Context

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing.

        Args:
            filters: The current dictionary of filters.

        Returns:
            The filters dictionary with studyKey injected if applicable.
        """
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters
