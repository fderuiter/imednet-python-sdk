"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from imednet.core.protocols import ParamProcessor


class DefaultParamProcessor(ParamProcessor):
    """
    Default parameter processor.

    Simply passes filters through without modification.
    """

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Return filters as-is and no special parameters.

        Args:
            filters: The input filters dictionary.

        Returns:
            A tuple of (copy of filters, empty dict).
        """
        return filters.copy(), {}


@dataclass
class ParamRule:
    """Rule for mapping a filter key to a parameter."""

    source: str
    target: str
    transform: Callable[[Any], Any] = field(default_factory=lambda: lambda x: x)
    default: Any = None
    skip_none: bool = True
    skip_falsey: bool = False


class MappingParamProcessor(ParamProcessor):
    """
    Declarative parameter processor.

    Iterates over defined rules to process filters, extracting special parameters.
    """

    rules: List[ParamRule] = []

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters based on configured rules.

        Args:
            filters: The input filters dictionary.

        Returns:
            A tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        special_params: Dict[str, Any] = {}

        for rule in self.rules:
            # Pop the source key if present, otherwise use default
            value = filters.pop(rule.source, rule.default)

            # If value is None and skip_none is True, skip
            if value is None and rule.skip_none:
                continue

            transformed = rule.transform(value)

            # If transformed value is falsey and skip_falsey is True, skip
            if not transformed and rule.skip_falsey:
                continue

            special_params[rule.target] = transformed

        return filters, special_params


class StudyKeyStrategy:
    """Strategy for handling study key extraction from filters."""

    def __init__(self, requires_study_key: bool, missing_exception: Type[Exception] = ValueError):
        self.requires_study_key = requires_study_key
        self.missing_exception = missing_exception

    def extract(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key from filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, filters_for_query).
        """
        raise NotImplementedError


class KeepStudyKeyStrategy(StudyKeyStrategy):
    """Strategy that keeps the study key in filters (validation only)."""

    def extract(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        filters = filters.copy()
        study = filters.get("studyKey")
        if not study and self.requires_study_key:
            raise self.missing_exception("Study key must be provided or set in the context")
        return study, filters


class PopStudyKeyStrategy(StudyKeyStrategy):
    """Strategy that pops the study key from filters."""

    def extract(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        filters = filters.copy()
        try:
            study = filters.pop("studyKey")
        except KeyError as exc:
            if self.requires_study_key:
                raise self.missing_exception(
                    "Study key must be provided or set in the context"
                ) from exc
            study = None

        return study, filters
