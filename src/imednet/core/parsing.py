"""
Centralized model parsing strategy for the iMednet SDK.

This module provides a consistent approach to parsing API responses into
Pydantic models, eliminating duplicated parsing logic across endpoints.
"""

from __future__ import annotations

from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel

__all__ = ["ModelParser", "get_model_parser"]


T = TypeVar("T", bound=BaseModel)


def get_model_parser(model: Type[T]) -> Callable[[Any], T]:
    """
    Return the appropriate parsing function for a model.

    This function implements a strategy pattern for model parsing:
    1. If the model has a custom `from_json` classmethod, use it
    2. Otherwise, fall back to Pydantic's `model_validate`

    Args:
        model: The model class to get a parser for

    Returns:
        A callable that takes raw data and returns a model instance

    Example:
        >>> from imednet.models.studies import Study
        >>> parser = get_model_parser(Study)
        >>> study = parser({"study_name": "Test", "study_key": "123"})
    """
    # Check for custom from_json method
    if hasattr(model, "from_json") and callable(getattr(model, "from_json")):
        return model.from_json  # type: ignore[attr-defined,return-value]

    # Fall back to Pydantic's model_validate
    return model.model_validate


class ModelParser:
    """
    Stateful parser that can be configured with a specific model.

    This class provides a convenient interface for repeated parsing
    operations with the same model type.

    Example:
        >>> from imednet.models.studies import Study
        >>> parser = ModelParser(Study)
        >>> studies = [parser.parse(data) for data in api_response]
    """

    def __init__(self, model: Type[BaseModel]) -> None:
        """
        Initialize parser with a model type.

        Args:
            model: The model class to parse data into
        """
        self.model = model
        self._parse_func: Callable[[Any], BaseModel] = get_model_parser(model)

    def parse(self, data: Any) -> BaseModel:
        """
        Parse raw data into a model instance.

        Args:
            data: Raw data (usually dict) to parse

        Returns:
            Parsed model instance
        """
        return self._parse_func(data)

    def parse_many(self, items: list[Any]) -> list[BaseModel]:
        """
        Parse a list of raw data items into model instances.

        Args:
            items: List of raw data items

        Returns:
            List of parsed model instances
        """
        return [self._parse_func(item) for item in items]
