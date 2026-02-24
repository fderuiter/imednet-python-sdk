"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Protocol, Tuple, Type

from imednet.core.protocols import ParamProcessor


class StudyKeyStrategy(Protocol):
    """Strategy for handling study key extraction and validation."""

    @property
    def is_required(self) -> bool:
        """Whether the study key is required."""
        ...

    def extract_study_key(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key from filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, modified_filters).
        """
        ...


class PopStudyKeyStrategy:
    """Strategy that removes studyKey from filters."""

    def __init__(self, exception_cls: Type[Exception] = ValueError) -> None:
        self.exception_cls = exception_cls

    @property
    def is_required(self) -> bool:
        return True

    def extract_study_key(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        filters = filters.copy()
        try:
            study_key = filters.pop("studyKey")
        except KeyError as exc:
            raise self.exception_cls("Study key must be provided or set in the context") from exc
        return study_key, filters


class KeepStudyKeyStrategy:
    """Strategy that keeps studyKey in filters."""

    def __init__(self, exception_cls: Type[Exception] = ValueError) -> None:
        self.exception_cls = exception_cls

    @property
    def is_required(self) -> bool:
        return True

    def extract_study_key(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        filters = filters.copy()
        study_key = filters.get("studyKey")
        if not study_key:
            raise self.exception_cls("Study key must be provided or set in the context")
        return study_key, filters


class OptionalStudyKeyStrategy:
    """Strategy where studyKey is optional and kept in filters."""

    @property
    def is_required(self) -> bool:
        return False

    def extract_study_key(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        return filters.get("studyKey"), filters.copy()


@dataclass
class ParamRule:
    """Rule for mapping a filter parameter."""

    input_key: str
    output_key: str
    default: Any = None
    transform: Optional[Callable[[Any], Any]] = None
    skip_none: bool = True
    skip_falsey: bool = False


class MappingParamProcessor(ParamProcessor):
    """Parameter processor using declarative mapping rules."""

    def __init__(self, rules: list[ParamRule]) -> None:
        self.rules = rules

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        filters = filters.copy()
        special_params = {}

        for rule in self.rules:
            value = filters.pop(rule.input_key, rule.default)

            if rule.skip_none and value is None:
                continue
            if rule.skip_falsey and not value:
                continue

            if rule.transform and value is not None:
                value = rule.transform(value)

            special_params[rule.output_key] = value

        return filters, special_params


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
