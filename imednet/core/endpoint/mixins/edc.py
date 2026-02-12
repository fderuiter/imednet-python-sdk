"""
Mixin for EDC-specific endpoint behavior.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, cast

from imednet.constants import EDC_BASE_PATH

if TYPE_CHECKING:
    from imednet.core.endpoint.base import BaseEndpoint


class EdcEndpointMixin:
    """
    Mixin for endpoints under the EDC API path.

    Provides the base path and default filter behavior (injecting study key).
    """

    BASE_PATH = EDC_BASE_PATH

    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Inject default studyKey if missing."""
        endpoint = cast("BaseEndpoint", self)
        if "studyKey" not in filters and endpoint._ctx.default_study_key:
            filters["studyKey"] = endpoint._ctx.default_study_key
        return filters
