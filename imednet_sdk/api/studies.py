"""API client for interacting with the iMednet Studies endpoints.

This module provides the `StudiesClient` class for accessing study-level
information via the iMednet API.
"""

import urllib.parse  # Add import
from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.study import StudyModel

from ..exceptions import ImednetSdkException
from ..models import ApiResponse, StudyModel
from ._base import ResourceClient


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

        Corresponds to `GET /studies`.

        Args:
            page: Optional page number (0-indexed) for pagination.
            size: Optional number of items per page for pagination.
            sort: Optional sorting criteria (e.g., "studyKey,asc").
            filter: Optional filter string (e.g., 'studyType=="STUDY"').
                    String values within the filter usually need to be enclosed
                    in double quotes (e.g., 'studyKey=="DEMO"').
            **kwargs: Additional parameters passed directly as query parameters.

        Returns:
            ApiResponse[list[StudyModel]]: An ApiResponse object containing a list
                                           of StudyModel instances and pagination info.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        params = kwargs  # Start with any extra kwargs
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            # Filters are often passed as is, let httpx handle encoding.
            # No special quoting applied here unless API docs specify otherwise.
            params["filter"] = filter

        # Use _get with constructed params
        # The response_model should be ApiResponse[List[StudyModel]]
        # Need to handle the generic ApiResponse structure correctly
        # The TypeAdapter in _request should handle ApiResponse[List[StudyModel]]
        return self._get(
            endpoint="/studies",
            response_model=ApiResponse[List[StudyModel]],  # Correct generic response model
            params=params,
        )

    def get_study_details(self, study_key: str) -> ApiResponse[StudyModel]:
        """
        Retrieves detailed information for a specific study.

        Corresponds to `GET /studies/{studyKey}`.

        Args:
            study_key (str): The unique key identifying the study.

        Returns:
            ApiResponse[StudyModel]: An ApiResponse object containing a single
                                     StudyModel instance.

        Raises:
            ImednetSdkException: If the API request fails (e.g., study not found).
        """
        # Use _get instead of _request
        return self._get(endpoint=f"/studies/{study_key}", response_model=StudyModel)

    def get_study_configuration(self, study_key: str) -> ApiResponse[dict]:
        """
        Retrieves the configuration details for a specific study.

        Corresponds to `GET /studies/{studyKey}/configuration`.

        Args:
            study_key (str): The unique key identifying the study.

        Returns:
            ApiResponse[dict]: An ApiResponse object containing the study configuration
                               as a dictionary. The exact structure may vary.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        # Assuming configuration returns a generic dictionary for now
        return self._get(
            endpoint=f"/studies/{study_key}/configuration",
            response_model=dict,  # Use dict if structure isn't strictly defined/modeled
        )

    def get_study_users(self, study_key: str, **kwargs) -> ApiResponse[list[dict]]:
        """
        Retrieves a list of users associated with a specific study.

        Corresponds to `GET /studies/{studyKey}/users`.

        Args:
            study_key (str): The unique key identifying the study.
            **kwargs: Additional parameters for filtering, pagination, sorting etc

        Returns:
            ApiResponse[list[dict]]: An ApiResponse object containing a list of user
                                     dictionaries. Consider creating a UserModel if needed.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        # Assuming user data returns as a list of dictionaries
        return self._get(
            endpoint=f"/studies/{study_key}/users",
            response_model=list[dict],  # Use list[dict] or create a UserModel
            params=kwargs,
        )
