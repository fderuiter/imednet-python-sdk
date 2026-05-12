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

    _id_param: str = "id"
    """
    The query parameter name for the ID.
    Defaults to "id". Override in subclasses if needed.
    """

    _enable_cache: bool = False
    """
    Whether this endpoint supports caching.
    Defaults to False. Override in subclasses if needed.
    """

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
            from imednet.errors.validation import ConfigurationError

            raise ConfigurationError(
                "No study key provided. You must either pass 'study_key' explicitly "
                "to the endpoint method or set it using ImednetSDK.study_context(...)."
            )

    def _get_endpoint_path(self, study_key: Optional[str], *extra_segments: Any) -> str:
        """
        Build the endpoint path with optional study key and extra segments.
        """
        self._validate_study_key(study_key)
        segments = []
        if self.requires_study_key:
            segments.append(study_key)
        if self.PATH:
            segments.append(self.PATH)
        segments.extend(extra_segments)
        return self._build_path(*segments)

    def _raise_not_found(self, study_key: Optional[str], item_id: Any = None) -> None:
        """
        Raise a standardized NotFoundError.
        """
        from imednet.errors import NotFoundError

        msg_parts = [f"{self.MODEL.__name__}"]
        if item_id is not None:
            msg_parts.append(str(item_id))
        msg_parts.append("not found")
        if self.requires_study_key and study_key:
            msg_parts.append(f"in study {study_key}")

        raise NotFoundError(" ".join(msg_parts))
