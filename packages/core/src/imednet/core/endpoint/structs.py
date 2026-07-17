"""Data structures for endpoint request state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from imednet.models.base import ImednetBaseModel

T = TypeVar("T", bound=ImednetBaseModel)


@dataclass
class ParamState:
    """Encapsulates the state of resolved parameters for an endpoint request.

    Attributes:
        study: The study key, if applicable.
        params: The dictionary of query parameters.
        other_filters: Remaining filters after study key extraction.
    """

    study: str | None
    params: dict[str, Any]
    other_filters: dict[str, Any]


@dataclass
class ListRequestState(Generic[T]):
    """Encapsulates the state required to execute a list request.

    Attributes:
        path: The API path for the request.
        params: The query parameters.
        study: The study key.
    """

    path: str
    params: dict[str, Any]
    study: str | None
