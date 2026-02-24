from __future__ import annotations

from typing import Any, Dict, Optional, Type, cast

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

    requires_study_key: bool = True
    _missing_study_exception: type[Exception] = ValueError

    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor
    STUDY_KEY_STRATEGY: Type[StudyKeyStrategy] = KeepStudyKeyStrategy

    # Backward compatibility for subclasses that haven't migrated
    _pop_study_filter: bool = False

    def _resolve_study_strategy(self) -> StudyKeyStrategy:
        """Resolve the study key strategy."""
        # If the class has overridden STUDY_KEY_STRATEGY, use it.
        if self.STUDY_KEY_STRATEGY is not KeepStudyKeyStrategy:
             return self.STUDY_KEY_STRATEGY(self.requires_study_key, self._missing_study_exception)

        # Fallback to checking legacy flag if strategy is default
        # But for cleaner refactor, we should assume subclasses are updated or we update them.
        # However, to be safe during refactor:
        if self._pop_study_filter:
            from imednet.core.endpoint.strategies import PopStudyKeyStrategy
            return PopStudyKeyStrategy(self.requires_study_key, self._missing_study_exception)

        return self.STUDY_KEY_STRATEGY(self.requires_study_key, self._missing_study_exception)

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

        strategy = self._resolve_study_strategy()
        study, query_filters = strategy.extract(filters)

        other_filters = {k: v for k, v in query_filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if query_filters:
            params["filter"] = build_filter_string(query_filters)
        if extra_params:
            params.update(extra_params)

        return ParamState(study=study, params=params, other_filters=other_filters)
