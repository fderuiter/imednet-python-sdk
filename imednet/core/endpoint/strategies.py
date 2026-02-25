"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from typing import Any, Dict, Optional, Protocol, Tuple, Type, runtime_checkable

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


@runtime_checkable
class StudyKeyStrategy(Protocol):
    """Protocol for study key handling strategies."""

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Process the study key from filters.

        Args:
            filters: The current filters dictionary.

        Returns:
            A tuple containing the extracted study key (if any) and the modified filters.
        """
        ...


class KeepStudyKeyStrategy:
    """
    Strategy that requires a study key and keeps it in the filters.

    Used when the API expects 'studyKey' as a query parameter.
    """

    def __init__(self, exception_cls: Type[Exception] = ValueError) -> None:
        self._exception_cls = exception_cls

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key, validate presence, and keep in filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, filters).

        Raises:
            Exception: If study key is missing (type determined by exception_cls).
        """
        study_key = filters.get("studyKey")
        if not study_key:
            raise self._exception_cls("Study key must be provided or set in the context")
        return study_key, filters


class PopStudyKeyStrategy:
    """
    Strategy that requires a study key but removes it from the filters.

    Used when the study key is part of the path or handled separately,
    not sent as a query parameter.
    """

    def __init__(self, exception_cls: Type[Exception] = ValueError) -> None:
        self._exception_cls = exception_cls

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key, validate presence, and remove from filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, modified_filters).

        Raises:
            Exception: If study key is missing (type determined by exception_cls).
        """
        # Ensure we work on a copy if we are modifying it,
        # but the mixin usually passes a copy or we should copy here.
        # ParamProcessor returns a copy, so filters here might be that copy.
        # But to be safe and pure:
        filters_copy = filters.copy()

        if "studyKey" not in filters_copy:
            raise self._exception_cls("Study key must be provided or set in the context")

        study_key = filters_copy.pop("studyKey")
        return study_key, filters_copy


class OptionalStudyKeyStrategy:
    """
    Strategy that allows the study key to be optional.

    If present, it is kept in the filters.
    """

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key if present.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key_or_none, filters).
        """
        study_key = filters.get("studyKey")
        return study_key, filters
