"""
Pydantic models and API client for iMednet “users”.

This module provides:

- `UserRole` and `UserModel`: Pydantic models representing user and role data.
- `UsersClient`: an API client for the `/api/v1/edc/studies/{study_key}/users` endpoint.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._base import ApiResponse, ResourceClient


class UserRole(BaseModel):
    """Represents a specific role assigned to a user within a study."""

    model_config = ConfigDict(populate_by_name=True)

    dateCreated: List[int] = Field(
        ..., alias="dateCreated", description="Raw [YYYY, MM, DD, HH, MM, SS, NNN] array"
    )
    dateModified: List[int] = Field(
        ..., alias="dateModified", description="Raw [YYYY, MM, DD, HH, MM, SS, NNN] array"
    )
    roleId: str = Field(..., description="Unique Role ID")
    communityId: int = Field(..., description="Community ID associated with the role")
    name: str = Field(..., description="Name of the role")
    description: str = Field(..., description="Description of the role")
    level: int = Field(..., description="Role level")
    type: str = Field(..., description="Type of role")
    inactive: bool = Field(False, description="Indicates if the role is inactive")

    @field_validator("dateCreated", "dateModified", mode="before")
    @classmethod
    def _validate_date_array(cls, v):
        if not isinstance(v, list) or len(v) < 6 or not all(isinstance(i, int) for i in v):
            raise ValueError("Date array must be a list of >=6 integers [YYYY, MM, DD, HH, MM, SS]")
        return v

    @property
    def created_datetime(self) -> datetime:
        return self._to_datetime(self.dateCreated)

    @property
    def modified_datetime(self) -> datetime:
        return self._to_datetime(self.dateModified)

    @classmethod
    def _to_datetime(cls, arr: List[int]) -> datetime:
        micro = (arr[6] // 1000) if len(arr) > 6 else 0
        return datetime(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5], micro)


class UserModel(BaseModel):
    """Represents a user account within the iMednet system, in a study context."""

    userId: str = Field(..., description="Unique User ID")
    login: str = Field(..., description="User login name")
    firstName: str = Field(..., description="User's first name")
    lastName: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    userActiveInStudy: bool = Field(..., description="Indicates if the user is active in the study")
    roles: List[UserRole] = Field(
        default_factory=list, description="List of roles assigned to the user"
    )


class UsersClient(ResourceClient):
    """Provides methods for accessing iMednet user data."""

    def list_users(
        self, study_key: str, include_inactive: bool = False, **kwargs
    ) -> ApiResponse[List[UserModel]]:
        """Retrieves a list of users associated with a specific study.

        GET /api/v1/edc/studies/{studyKey}/users
        Supports pagination, sorting, and optional inclusion of inactive users.

        Args:
            study_key: The unique identifier for the study.
            include_inactive: If True, include inactive users. Defaults to False.
            **kwargs: Additional query params (e.g. page, size, sort).

        Returns:
            ApiResponse[List[UserModel]] with users and pagination metadata.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors (network, auth, permissions).
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/users"
        params = {**kwargs, "includeInactive": include_inactive}

        response: ApiResponse[List[UserModel]] = self._get(
            endpoint,
            params=params,
            response_model=ApiResponse[List[UserModel]],
        )
        return response
