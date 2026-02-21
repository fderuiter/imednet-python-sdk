"""
Parameter processing strategies for endpoints.

This module implements the ParamProcessor strategy pattern, allowing endpoints
to customize how filters are processed and special parameters are extracted.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

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
    """
    Rule for mapping a filter key to a special parameter.

    Attributes:
        input_key: The filter key to extract.
        output_key: The parameter key to use in the special parameters.
        default: The default value to use if the input key is missing.
        transform: An optional function to transform the value.
        skip_none: If True, do not include the parameter if the value is None.
        skip_falsey: If True, do not include the parameter if the value is falsey.
    """

    input_key: str
    output_key: str
    default: Any = None
    transform: Optional[Callable[[Any], Any]] = None
    skip_none: bool = True
    skip_falsey: bool = False


class MappingParamProcessor(ParamProcessor):
    """
    Parameter processor that maps filters based on declarative rules.

    Subclasses should define the `rules` attribute.
    """

    rules: List[ParamRule] = []

    def process_filters(self, filters: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Process filters using the configured rules.

        Args:
            filters: The input filters dictionary.

        Returns:
            A tuple of (cleaned filters, special parameters).
        """
        filters = filters.copy()
        special_params = {}

        for rule in self.rules:
            # Extract value using the rule's input key and default
            value = filters.pop(rule.input_key, rule.default)

            if rule.transform:
                try:
                    value = rule.transform(value)
                except Exception:
                    raise

            should_skip = False
            if rule.skip_falsey and not value:
                should_skip = True
            elif rule.skip_none and value is None:
                should_skip = True

            if not should_skip:
                special_params[rule.output_key] = value

        return filters, special_params
