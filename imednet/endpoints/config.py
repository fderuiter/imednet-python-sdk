"""
Endpoint configuration and metadata.

This module provides structured configuration for API endpoints,
centralizing common patterns and defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type

__all__ = ["EndpointConfig"]


@dataclass
class EndpointConfig:
    """
    Configuration for an API endpoint.

    This class centralizes common endpoint configuration options,
    making it easier to understand and modify endpoint behavior.

    Attributes:
        path: The API path for this endpoint (e.g., "records", "studies")
        id_param: The parameter name used for filtering by ID (e.g., "recordId")
        cache_name: Optional name for caching this endpoint's data
        page_size: Number of items to fetch per page (default: 100)
        pop_study_filter: Whether to remove studyKey from filters after extraction
        missing_study_exception: Exception to raise when study key is missing
        requires_study_key: Whether this endpoint requires a study key
    """

    path: str
    id_param: str
    cache_name: Optional[str] = None
    page_size: int = 100
    pop_study_filter: bool = False
    missing_study_exception: Type[Exception] = ValueError
    requires_study_key: bool = True


# Common configuration presets
STUDY_SCOPED_CONFIG = EndpointConfig(
    path="",  # Override in subclass
    id_param="id",  # Override in subclass
    pop_study_filter=True,
    missing_study_exception=KeyError,
    requires_study_key=True,
)

CACHED_METADATA_CONFIG = EndpointConfig(
    path="",  # Override in subclass
    id_param="id",  # Override in subclass
    page_size=500,
    pop_study_filter=True,
    requires_study_key=True,
)
