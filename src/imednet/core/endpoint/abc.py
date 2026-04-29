"""Abstract base class for all API endpoints."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Optional, Type, TypeVar

from imednet.core.protocols import ClientProvider
from imednet.models.json_base import JsonModel

T = TypeVar("T", bound=JsonModel)


class EndpointABC(ABC, ClientProvider, Generic[T]):
    """
    Abstract base class defining the contract for all API endpoints.

    This ensures that all endpoint implementations provide necessary
    properties like PATH and MODEL, and implement core path building logic.
    """

    @property
    @abstractmethod
    def PATH(self) -> str:  # noqa: N802
        """The relative path for the endpoint."""
        pass

    @property
    @abstractmethod
    def MODEL(self) -> Type[T]:  # noqa: N802
        """The model class associated with this endpoint."""
        pass

    requires_study_key: bool = True
    """
    Whether this endpoint requires a study key.
    Defaults to True. Override in subclasses if needed.
    """

    @property
    def _id_param(self) -> str:
        """
        The query parameter name for the ID.
        Defaults to "id". Override in subclasses if needed.
        """
        return "id"

    @property
    def _enable_cache(self) -> bool:
        """
        Whether this endpoint supports caching.
        Defaults to False. Override in subclasses if needed.
        """
        return False

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

    def _validate_study_key(self, study_key: Optional[str]) -> None:
        """Validate that a study key is provided if required."""
        if self.requires_study_key and not study_key:
            from imednet.errors import ClientError

            raise ClientError("Study key must be provided or set in the context")
