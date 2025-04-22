"""
Pydantic model and API client for iMednet “sites”.

This module provides:

- `SiteModel`: a Pydantic model representing site metadata.
- `SitesClient`: an API client for the `/api/v1/edc/studies/{study_key}/sites` endpoint.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class SiteModel(BaseModel):
    """Represents a clinical research site within a study in iMednet."""

    studyKey: str = Field(..., description="Unique study key for the given study")
    siteId: int = Field(..., description="Unique system identifier for the site")
    siteName: str = Field(..., description="Name of the site")
    siteEnrollmentStatus: str = Field(..., description="Current enrollment status of the site")
    dateCreated: datetime = Field(..., description="Date when the site record was created")
    dateModified: datetime = Field(..., description="Last modification date of the site record")


class SitesClient(ResourceClient):
    """Provides methods for accessing iMednet site data."""

    def list_sites(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[SiteModel]]:
        """Retrieves a list of sites for a specific study.

        GET /api/v1/edc/studies/{studyKey}/sites
        Supports pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort property and direction (e.g., 'siteName,asc').
            filter: Filter expression (e.g., 'siteStatus=="Active"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[SiteModel]] containing sites and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors (network, auth, permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/sites"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter
        params.update(kwargs)

        # Cast the result to the expected type
        response = cast(
            ApiResponse[List[SiteModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[SiteModel]],
            ),
        )
        return response
