from __future__ import annotations

from typing import Any, Generic, Type, TypeVar

from imednet.core.parsing import get_model_parser
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class ParsingMixin(Generic[T]):
    """Mixin implementing model parsing helpers."""

    MODEL: Type[T]

    def _parse_item(self, item: Any) -> T:
        """
        Parse a single item into the model type.

        This method can be overridden by subclasses for custom parsing logic.
        By default, it uses the centralized parsing strategy.

        Args:
            item: Raw data to parse

        Returns:
            Parsed model instance
        """
        parse_func = get_model_parser(self.MODEL)
        return parse_func(item)
