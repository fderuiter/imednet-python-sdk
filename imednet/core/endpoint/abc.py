"""Abstract base class for all API endpoints."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class EndpointABC(ABC, Generic[T]):
    """
    Abstract base class defining the contract for all API endpoints.

    This ensures that all endpoint implementations provide necessary
    properties like PATH and MODEL, and implement core path building logic.
    """

    @property
    @abstractmethod
    def PATH(self) -> str:
        """The relative path for the endpoint."""
        pass

    @property
    @abstractmethod
    def MODEL(self) -> Type[T]:
        """The model class associated with this endpoint."""
        pass

    @property
    def requires_study_key(self) -> bool:
        """
        Whether this endpoint requires a study key.
        Defaults to True. Override in subclasses if needed.
        """
        return True

    @property
    def _id_param(self) -> str:
        """
        The query parameter name for the ID.
        Defaults to "id". Override in subclasses if needed.
        """
        return "id"

    @property
    def _cache_name(self) -> Optional[str]:
        """
        The name of the attribute used for caching results.
        Defaults to None (no caching).
        """
        return None

    @abstractmethod
    def _build_path(self, *segments: Any) -> str:
        """
        Build the full API path given segments.
        Must be implemented by the base endpoint logic.
        """
        pass

    @abstractmethod
    def _auto_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply automatic filters (e.g., default study key).
        Must be implemented by the base endpoint logic.
        """
        pass
