from __future__ import annotations

from typing import Any, Dict, Optional, cast

from imednet.core.endpoint.structs import ParamState
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
    ) -> ParamState:
        # Create a copy of filters to avoid mutating the input
        # Note: We copy shallowly which is enough for typical filter dicts
        working_filters = filters.copy()

        # Inject default filters (e.g., study key)
        # This might add 'studyKey' to working_filters if missing
        working_filters = cast(EndpointProtocol, self)._auto_filter(working_filters)

        # Extract special parameters using the hook
        # This might remove keys from working_filters (e.g. include_inactive)
        special_params = self._extract_special_params(working_filters)

        # Prepare params to be sent
        params: Dict[str, Any] = {}
        if extra_params:
            params.update(extra_params)
        if special_params:
            params.update(special_params)

        # Ensure study_key is present in working_filters if provided explicitly via argument
        if study_key:
            working_filters["studyKey"] = study_key

        # Resolve study context
        study: Optional[str] = None
        if self.requires_study_key:
            study = working_filters.get("studyKey")
            if not study:
                raise self._missing_study_exception(
                    "Study key must be provided or set in the context"
                )
        else:
            study = working_filters.get("studyKey")

        # Determine if studyKey should be in the filter string
        # If _pop_study_filter is True, we remove it from filters used for string generation.
        # If False, we keep it (e.g. for RecordsEndpoint).
        filters_for_string = working_filters.copy()
        if self._pop_study_filter and "studyKey" in filters_for_string:
            del filters_for_string["studyKey"]

        # other_filters excludes studyKey regardless of _pop_study_filter setting
        # (Used for cache key generation or logic relying on non-study filters)
        other_filters = {k: v for k, v in working_filters.items() if k != "studyKey"}

        if filters_for_string:
            params["filter"] = build_filter_string(filters_for_string)

        return ParamState(study=study, params=params, other_filters=other_filters)
