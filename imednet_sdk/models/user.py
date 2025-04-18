"""User-related data models."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class UserRole(BaseModel):
    """Model representing a user's role in the study."""
    model_config = ConfigDict(populate_by_name=True)
    dateCreated: List[int] = Field(..., alias="dateCreated", description="Date array when the role was created")
    dateModified: List[int] = Field(..., alias="dateModified", description="Date array when the role was last modified")
    roleId: str = Field(..., description="Unique Role ID")

    @property
    def dateCreated(self) -> datetime:
        """Convert date array to datetime object."""
        return self.from_date_array(self._dateCreated)

    @property
    def dateModified(self) -> datetime:
        """Convert date array to datetime object."""
        return self.from_date_array(self._dateModified)
    communityId: int = Field(..., description="Community ID associated with the role")
    name: str = Field(..., description="Name of the role")
    description: str = Field(..., description="Description of the role")
    level: int = Field(..., description="Role level")
    type: str = Field(..., description="Type of role")
    inactive: bool = Field(False, description="Indicates if the role is inactive")

    @classmethod
    def from_date_array(cls, date_array: List[int]) -> datetime:
        """Convert a date array [YYYY, MM, DD, HH, MM, SS, NNNNNNNNN] to datetime."""
        if len(date_array) >= 6:
            return datetime(
                year=date_array[0],
                month=date_array[1],
                day=date_array[2],
                hour=date_array[3],
                minute=date_array[4],
                second=date_array[5],
                microsecond=date_array[6] // 1000 if len(date_array) > 6 else 0,
            )
        raise ValueError("Invalid date array format")


class UserModel(BaseModel):
    """Model representing a user in the iMednet system."""

    userId: str = Field(..., description="Unique User ID")
    login: str = Field(..., description="User login name")
    firstName: str = Field(..., description="User's first name")
    lastName: str = Field(..., description="User's last name")
    email: str = Field(..., description="User's email address")
    userActiveInStudy: bool = Field(..., description="Indicates if the user is active in the study")
    roles: List[UserRole] = Field(
        default_factory=list, description="List of user's roles in the study"
    )
