"""API client for interacting with the iMednet Studies endpoints.

This module provides the `StudiesClient` class for accessing study-level
information via the iMednet API.
"""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.study import StudyModel

from ..exceptions import ImednetSdkException
from ..models import ApiResponse, StudyModel
from ._base import ResourceClient


class StudiesClient(ResourceClient):
    """Client for interacting with iMednet Study endpoints."""

    def list_studies(self, **kwargs) -> ApiResponse[list[StudyModel]]:
        """
        Retrieves a list of studies based on specified criteria.

        Corresponds to `GET /studies`.

        Args:
            **kwargs: Additional parameters for filtering, pagination, sorting etc.
                      (e.g., filter, page, size, sort).

        Returns:
            ApiResponse[list[StudyModel]]: An ApiResponse object containing a list
                                           of StudyModel instances and pagination info.

        Raises:
            ImednetSdkException: If the API request fails.
        """
        # Use _get instead of _request
        return self._get(
            endpoint="/studies", response_model=list[StudyModel], params=kwargs
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
        return self._get(
            endpoint=f"/studies/{study_key}", response_model=StudyModel
        )

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
            **kwargs: Additional parameters for filtering, pagination, sorting etc.

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
