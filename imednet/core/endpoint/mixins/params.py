from __future__ import annotations

from typing import Any, Dict, Optional, cast

from imednet.utils.filters import build_filter_string
from ..protocols import EndpointProtocol


class ParamMixin:
    """Mixin for handling endpoint parameters and filters."""

    requires_study_key: bool = True
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    def _extract_special_params(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook to extract special parameters from filters.

        Subclasses should override this method to handle parameters that need to be
        passed separately (e.g. in extra_params) rather than in the filter string.
        These parameters should be removed from the filters dictionary.
        """
        return {}

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> tuple[Optional[str], Dict[str, Any], Dict[str, Any]]:
        # This method handles filter normalization and cache retrieval preparation
        # Assuming _auto_filter is available via self (EndpointProtocol)
        filters = cast(EndpointProtocol, self)._auto_filter(filters)

        # Extract special parameters using the hook
        special_params = self._extract_special_params(filters)

        if special_params:
            if extra_params is None:
                extra_params = {}
            extra_params.update(special_params)

        if study_key:
            filters["studyKey"] = study_key

        study: Optional[str] = None
        if self.requires_study_key:
            if self._pop_study_filter:
                try:
                    study = filters.pop("studyKey")
                except KeyError as exc:
                    raise self._missing_study_exception(
                        "Study key must be provided or set in the context"
                    ) from exc
            else:
                study = filters.get("studyKey")
                if not study:
                    raise ValueError("Study key must be provided or set in the context")
        else:
            study = filters.get("studyKey")

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        return study, params, other_filters
