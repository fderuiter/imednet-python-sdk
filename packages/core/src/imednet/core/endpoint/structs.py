"""TODO: Add docstring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, TypeVar

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


@dataclass
class ParamState:
    """Encapsulates the state of resolved parameters for an endpoint request.

    Attributes:
        study: The study key, if applicable.
        params: The dictionary of query parameters.
        other_filters: Remaining filters after study key extraction.
    """

    study: Optional[str]
    params: Dict[str, Any]
    other_filters: Dict[str, Any]


@dataclass
class ListRequestState(Generic[T]):
    """Encapsulates the state required to execute a list request.

    Attributes:
        path: The API path for the request.
        params: The query parameters.
        study: The study key.
    """

    path: str
    params: Dict[str, Any]
    study: Optional[str]
