"""
Pydantic model and API client for iMednet “studies”.

This module provides:

- `StudyModel`: a Pydantic model representing study metadata.
- `StudiesClient`: an API client for `/studies` and `/studies/{study_key}/users` endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ._base import ApiResponse, ResourceClient


class StudyModel(BaseModel):
    """Represents a clinical study defined within the iMednet system."""

    sponsorKey: str = Field(..., description="Sponsor key that this study belongs to")
    studyKey: str = Field(..., description="Unique study key")
    studyId: int = Field(..., description="Mednet study ID")
    studyName: str = Field(..., description="Study name")
    studyDescription: Optional[str] = Field(None, description="Detailed description of the study")
    studyType: str = Field(..., description="Type of the study")
    dateCreated: datetime = Field(..., description="Date when the study record was created")
    dateModified: datetime = Field(..., description="Last modification date of the study record")


class StudiesClient(ResourceClient):
    """Client for interacting with iMednet Study endpoints."""

    def list_studies(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[StudyModel]]:
        """
        Retrieves a list of studies based on specified criteria.

        GET /studies

        Args:
            page: Optional page number (0-indexed) for pagination.
            size: Optional number of items per page.
            sort: Optional sorting criteria (e.g., "studyKey,asc").
            filter: Optional filter string (e.g., 'studyType=="STUDY"').
            **kwargs: Additional query parameters.

        Returns:
            ApiResponse[List[StudyModel]] containing studies and pagination info.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        params = {**kwargs}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter

        response: ApiResponse[List[StudyModel]] = self._get(
            endpoint="/studies",
            params=params,
            response_model=ApiResponse[List[StudyModel]],
        )
        return response

    def get_study_users(self, study_key: str, **kwargs: Any) -> ApiResponse[List[Dict[Any, Any]]]:
        """
        Retrieves a list of users associated with a specific study.

        GET /studies/{studyKey}/users

        Args:
            study_key: The unique key identifying the study.
            **kwargs: Additional query parameters (pagination, sorting, filters).

        Returns:
            ApiResponse[List[dict]] containing user dictionaries.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        response: ApiResponse[List[Dict[Any, Any]]] = self._get(
            endpoint=f"/studies/{study_key}/users",
            params=kwargs,
            response_model=ApiResponse[List[Dict[Any, Any]]],
        )
        return response
