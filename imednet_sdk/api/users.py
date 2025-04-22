"""API client for interacting with the iMednet Users endpoints.

This module provides the `UsersClient` class for accessing user information
within a specific study via the iMednet API.
"""

from typing import List

from ..models._common import ApiResponse
from ..models.user import UserModel
from ._base import ResourceClient


class UsersClient(ResourceClient):
    """Provides methods for accessing iMednet user data.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/users`.
    It is accessed via the `imednet_sdk.client.ImednetClient.users` property.
    """

    def list_users(
        self, study_key: str, include_inactive: bool = False, **kwargs
    ) -> ApiResponse[List[UserModel]]:
        """Retrieves a list of users associated with a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/users` endpoint.
        Supports standard pagination and sorting parameters, plus an option
        to include inactive users.

        Args:
            study_key: The unique identifier for the study.
            include_inactive: If True, includes users marked as inactive in the results.
                              Defaults to False.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request, such as `page`, `size`, `sort`.
                      Refer to the iMednet API documentation for available options.

        Returns:
            An `ApiResponse` object containing a list of `UserModel` instances
            representing the users, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/users"
        params = kwargs.copy()
        params["includeInactive"] = include_inactive

        return self._get(endpoint, params=params, response_model=ApiResponse[list[UserModel]])
