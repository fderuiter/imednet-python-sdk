"""Pydantic models related to iMednet Users and Roles.

This module defines the Pydantic models `UserRole` and `UserModel` which
represent the structure of user and role information retrieved from the
iMednet API, typically via the `/users` endpoint.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRole(BaseModel):
    """Represents a specific role assigned to a user within a study.

    Handles the conversion of iMednet's date array format for creation and
    modification timestamps into standard Python `datetime` objects via properties.

    Attributes:
        dateCreated (List[int]): Raw date array [YYYY, MM, DD, HH, MM, SS, NNNNNNNNN]
                                 from the API representing when the role was created.
                                 Use the `created_datetime` property for a `datetime` object.
        dateModified (List[int]): Raw date array [YYYY, MM, DD, HH, MM, SS, NNNNNNNNN]
                                  from the API representing when the role was last modified.
                                  Use the `modified_datetime` property for a `datetime` object.
        roleId (str): Unique string identifier for the role definition.
        communityId (int): Numeric identifier for the community associated with the role.
        name (str): The name of the role (e.g., "Data Manager", "Investigator").
        description (str): A description of the role's purpose or permissions.
        level (int): A numeric level associated with the role.
        type (str): The type category of the role.
        inactive (bool): Boolean flag indicating if the role definition itself is inactive.
    """

    model_config = ConfigDict(populate_by_name=True)
    # Use original names, rely on alias for input mapping
    dateCreated: List[int] = Field(
        ..., alias="dateCreated", description="Date array when the role was created"
    )
    dateModified: List[int] = Field(
        ..., alias="dateModified", description="Date array when the role was last modified"
    )
    roleId: str = Field(..., description="Unique Role ID")

    @field_validator("dateCreated", "dateModified", mode="before")
    @classmethod
    def check_date_array_format(cls, v):
        """Validates that the input date array has the expected format."""
        # Validator receives the raw input value due to mode='before'
        if not isinstance(v, list) or len(v) < 6:
            raise ValueError(
                "Date array must be a list with at least 6 integer elements "
                "(YYYY, MM, DD, HH, MM, SS)"
            )
        # Optionally, add type check for elements if needed
        # if not all(isinstance(i, int) for i in v):
        #     raise ValueError("All elements in date array must be integers")
        return v

    @property
    def created_datetime(self) -> datetime:
        """Provides the role creation timestamp as a standard `datetime` object."""
        # Access the validated list stored in the field
        return self._from_date_array(self.dateCreated)

    @property
    def modified_datetime(self) -> datetime:
        """Provides the role modification timestamp as a standard `datetime` object."""
        # Access the validated list stored in the field
        return self._from_date_array(self.dateModified)

    communityId: int = Field(..., description="Community ID associated with the role")
    name: str = Field(..., description="Name of the role")
    description: str = Field(..., description="Description of the role")
    level: int = Field(..., description="Role level")
    type: str = Field(..., description="Type of role")
    inactive: bool = Field(False, description="Indicates if the role is inactive")

    @classmethod
    def _from_date_array(cls, date_array: List[int]) -> datetime:
        """Internal helper to convert a validated date array to a datetime object."""
        try:
            return datetime(
                year=date_array[0],
                month=date_array[1],
                day=date_array[2],
                hour=date_array[3],
                minute=date_array[4],
                second=date_array[5],
                microsecond=date_array[6] // 1000 if len(date_array) > 6 else 0,
            )
        except (TypeError, IndexError) as e:
            # This should ideally not happen if validator works correctly
            raise ValueError(f"Error converting validated date array: {e}") from e


class UserModel(BaseModel):
    """Represents a user account within the iMednet system, specific to a study context.

    Attributes:
        userId: Unique string identifier assigned by iMednet to the user.
        login: The username used for logging in.
        firstName: The user's first name.
        lastName: The user's last name.
        email: The user's email address.
        userActiveInStudy: Boolean flag indicating if the user is currently active
                           within the specific study context.
        roles: A list of `UserRole` objects representing the roles assigned to this
               user within the study.
    """

    userId: str = Field(..., description="Unique User ID")
    login: str = Field(..., description="User login name")
    firstName: str = Field(..., description="User's first name")
    lastName: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    userActiveInStudy: bool = Field(..., description="Indicates if the user is active in the study")
    roles: List[UserRole] = Field(
        default_factory=list, description="List of user's roles in the study"
    )
