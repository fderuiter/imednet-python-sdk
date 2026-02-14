"""
Mixin for EDC-specific endpoint logic.

This mixin provides the base path for EDC endpoints and handles the injection
of the default study key into request filters.
"""

from __future__ import annotations

from typing import Any, Dict

from imednet.core.context import Context


class EdcEndpointMixin:
    """
    Mixin for endpoints interacting with the EDC API.

    Provides the base path `/api/v1/edc/studies` and injects the default study key
    if available in the context.
    """

    BASE_PATH = "/api/v1/edc/studies"

    # Type hint for context which is expected to be present on the instance
    _ctx: Context

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing from filters.

        Args:
            filters: The current dictionary of filters/parameters.

        Returns:
            The updated dictionary with studyKey injected if available.
        """
        # inject default studyKey if missing
        if "studyKey" not in filters and self._ctx.default_study_key:
            filters["studyKey"] = self._ctx.default_study_key
        return filters
