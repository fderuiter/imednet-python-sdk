from __future__ import annotations

from typing import Any, Dict, Optional, cast

from imednet.core.endpoint.strategies import (
    DefaultParamProcessor,
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
    StudyKeyStrategy,
)
from imednet.core.endpoint.structs import ParamState
from imednet.core.protocols import ParamProcessor
from imednet.errors import ClientError
from imednet.utils.filters import build_filter_string

from ..protocols import EndpointProtocol


class ParamMixin:
    """Mixin for handling endpoint parameters and filters."""

    requires_study_key: bool = True

    PARAM_PROCESSOR: Optional[ParamProcessor] = None
    PARAM_PROCESSOR_CLS: type[ParamProcessor] = DefaultParamProcessor
    STUDY_KEY_STRATEGY: Optional[StudyKeyStrategy] = None

    @property
    def study_key_strategy(self) -> StudyKeyStrategy:
        """
        Get the configured study key strategy.

        Returns:
            The strategy instance to use.
        """
        if self.STUDY_KEY_STRATEGY:
            return self.STUDY_KEY_STRATEGY

        if self.requires_study_key:
            return KeepStudyKeyStrategy(exception_cls=ClientError)
        return OptionalStudyKeyStrategy()

    @property
    def param_processor(self) -> ParamProcessor:
        """
        Get the configured parameter processor.

        Returns:
            The processor instance to use.
        """
        if self.PARAM_PROCESSOR:
            return self.PARAM_PROCESSOR
        return self.PARAM_PROCESSOR_CLS()

    def _resolve_params(
        self,
        study_key: Optional[str],
        extra_params: Optional[Dict[str, Any]],
        filters: Dict[str, Any],
    ) -> ParamState:
        # Prevent hidden mutable state by safely copying the dictionary
        filters = filters.copy()

        # This method handles filter normalization and cache retrieval preparation
        # Assuming _auto_filter is available via self (EndpointProtocol)
        filters = cast(EndpointProtocol, self)._auto_filter(filters)

        # Use the configured parameter processor strategy
        processor = self.param_processor
        filters, special_params = processor.process_filters(filters)

        if special_params:
            if extra_params is None:
                extra_params = {}
            else:
                extra_params = extra_params.copy()
            extra_params.update(special_params)

        if study_key:
            filters["studyKey"] = study_key

        # Delegate study key handling to the strategy
        study, filters = self.study_key_strategy.process(filters)

        other_filters = {k: v for k, v in filters.items() if k != "studyKey"}

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        if extra_params:
            params.update(extra_params)

        return ParamState(study=study, params=params, other_filters=other_filters)


class PopStudyKeyMixin(ParamMixin):
    """
    Mixin for endpoints that require a study key in the path but not in filters.

    This explicitly sets the study key strategy to :class:`PopStudyKeyStrategy`,
    which enforces that a study key must be provided but removes it from the
    filters dictionary, typically because it will be injected into the URL path.
    """

    STUDY_KEY_STRATEGY: Optional[StudyKeyStrategy] = PopStudyKeyStrategy(exception_cls=ClientError)
