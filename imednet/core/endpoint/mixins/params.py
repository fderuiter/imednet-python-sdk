from __future__ import annotations

from typing import Any, Dict, Optional, cast

from imednet.core.endpoint.strategies import (
    DefaultParamProcessor,
    KeepStudyKeyStrategy,
    StudyKeyStrategy,
)
from imednet.core.endpoint.structs import ParamState
from imednet.core.protocols import ParamProcessor
from imednet.utils.filters import build_filter_string

from ..protocols import EndpointProtocol


class ParamMixin:
    """Mixin for handling endpoint parameters and filters."""

    # Default strategy: Keep studyKey, raise ValueError if missing
    STUDY_KEY_STRATEGY: StudyKeyStrategy = KeepStudyKeyStrategy(ValueError)

    PARAM_PROCESSOR: Optional[ParamProcessor] = None
    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor

    @property
    def requires_study_key(self) -> bool:
        """Whether this endpoint requires a study key."""
        return self.STUDY_KEY_STRATEGY.is_required

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
        processor = self.PARAM_PROCESSOR or self.PARAM_PROCESSOR_CLS()
        filters, special_params = processor.process_filters(filters)

        if special_params:
            if extra_params is None:
                extra_params = {}
            extra_params.update(special_params)

        if study_key:
            filters["studyKey"] = study_key

        study, filters = self.STUDY_KEY_STRATEGY.extract_study_key(filters)

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        return ParamState(study=study, params=params, other_filters=other_filters)
