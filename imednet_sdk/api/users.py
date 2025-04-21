# API client for interacting with iMednet Users endpoints.

from typing import List

from ..models._common import ApiResponse
from ..models.user import UserModel
from ._base import ResourceClient


class UsersClient(ResourceClient):
    """Client for managing users within a study."""

    def list_users(
        self, study_key: str, include_inactive: bool = False, **kwargs
    ) -> ApiResponse[List[UserModel]]:
        """Lists users for a specific study.

        Args:
            study_key (str): The key identifying the study.
            include_inactive (bool, optional): Whether to include inactive users.
                                               Defaults to False.
            **kwargs: Optional keyword arguments for pagination, sorting, etc.
                      (e.g., page, size, sort).

        Returns:
            ApiResponse[List[UserModel]]: An API response object containing a list
                                          of users and metadata.

        Raises:
            ValueError: If study_key is not provided.
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/users"
        params = kwargs.copy()
        params["includeInactive"] = str(
            include_inactive
        ).lower()  # API expects string 'true'/'false'

        return self._client._get(
            endpoint, params=params, response_model=ApiResponse[List[UserModel]]
        )
