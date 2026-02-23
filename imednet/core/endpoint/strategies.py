"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from imednet.core.protocols import ParamProcessor


@dataclass
class ParamRule:
    """
    Rule for mapping a filter key to an API parameter.

    Attributes:
        filter_key: The key in the input filters dictionary.
        param_key: The key for the API parameter.
        default: Default value if key is missing in filters.
        transform: Optional function to transform the value.
        skip_none: Whether to skip if value is None.
        skip_falsey: Whether to skip if value is falsey (e.g., False, 0, empty list).
    """

    filter_key: str
    param_key: str
    default: Any = None
    transform: Optional[Callable[[Any], Any]] = None
    skip_none: bool = True
    skip_falsey: bool = False


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
    Declarative parameter processor.

    Maps filter keys to API parameter keys based on a provided list of rules.
    """

    RULES: List[ParamRule] = []

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters by applying mapping rules.

        Args:
            filters: The input filters dictionary.

        Returns:
            A tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        special_params = {}

        for rule in self.RULES:
            # Extract value, using default if missing
            value = filters.pop(rule.filter_key, rule.default)

            # Apply transformation
            if rule.transform is not None:
                value = rule.transform(value)

            # Check skip conditions
            if rule.skip_none and value is None:
                continue
            if rule.skip_falsey and not value:
                continue

            special_params[rule.param_key] = value

        return filters, special_params
