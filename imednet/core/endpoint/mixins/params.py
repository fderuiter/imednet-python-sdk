from __future__ import annotations

from typing import Any, Dict, Optional, cast

from imednet.core.endpoint.strategies import DefaultParamProcessor
from imednet.core.endpoint.structs import ParamState
from imednet.core.protocols import ParamProcessor
from imednet.utils.filters import build_filter_string

from ..protocols import EndpointProtocol


class ParamMixin:
    """Mixin for handling endpoint parameters and filters."""

    requires_study_key: bool = True
    _pop_study_filter: bool = False
    _missing_study_exception: type[Exception] = ValueError

    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ParamState:
        # This method handles filter normalization and cache retrieval preparation
        # Assuming _auto_filter is available via self (EndpointProtocol)
        filters = cast(EndpointProtocol, self)._auto_filter(filters)

        # Use the configured parameter processor strategy
        processor = self.PARAM_PROCESSOR_CLS()
        filters, special_params = processor.process_filters(filters)

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

        return ParamState(study=study, params=params, other_filters=other_filters)
