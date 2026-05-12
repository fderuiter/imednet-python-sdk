"""Mixin for EDC-specific endpoint logic."""

from __future__ import annotations

from typing import Any, Dict

from imednet.core.context import get_study_context


class EdcEndpointMixin:
    """
    Mixin providing EDC-specific logic for endpoints.

    This includes the base path for EDC resources and automatic injection
    of the default study key into filters.
    """

    BASE_PATH = "/api/v1/edc/studies"

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject default studyKey if missing.

        Args:
            filters: The current dictionary of filters.

        Returns:
            The filters dictionary with studyKey injected if applicable.
        """
        study_key = get_study_context()
        if "studyKey" not in filters and study_key:
            filters["studyKey"] = study_key
        return filters
