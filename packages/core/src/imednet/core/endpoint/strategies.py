"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable

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


class MappingParamProcessor(ParamProcessor):
    """
    ParamProcessor that maps specific filter keys to API parameters.

    Extracts keys defined in the mapping and returns them as special parameters,
    optionally renaming them according to the mapping values.
    """

    def __init__(
        self,
        mapping: Dict[str, str],
        defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the processor with a mapping.

        Args:
            mapping: A dictionary where keys are the filter keys to look for,
                     and values are the API parameter names to map them to.
            defaults: A dictionary of default values for keys not found in filters.
        """
        self.mapping = mapping
        self.defaults = defaults or {}

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters using the configured mapping.

        Args:
            filters: The input filters dictionary.

        Returns:
            A tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        special_params = {}

        for filter_key, api_key in self.mapping.items():
            value = None
            if filter_key in filters:
                value = filters.pop(filter_key)
            elif filter_key in self.defaults:
                value = self.defaults[filter_key]

            if value is not None:
                # Convert boolean to lowercase string if necessary, or just pass through
                if isinstance(value, bool):
                    special_params[api_key] = str(value).lower()
                else:
                    special_params[api_key] = value

        return filters, special_params


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

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key and keep in filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, filters).
        """
        study_key = filters.get("studyKey")
        return study_key, filters


class PopStudyKeyStrategy:
    """
    Strategy that requires a study key but removes it from the filters.

    Used when the study key is part of the path or handled separately,
    not sent as a query parameter.
    """

    def process(self, filters: Dict[str, Any]) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Extract study key and remove from filters.

        Args:
            filters: The filters dictionary.

        Returns:
            Tuple of (study_key, modified_filters).
        """
        filters_copy = filters.copy()
        study_key = filters_copy.pop("studyKey", None)
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
