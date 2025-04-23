from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Role:
    date_created: list[int]
    date_modified: list[int]
    role_id: str
    community_id: int
    name: str
    description: str
    level: int
    type: str
    inactive: bool

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Role":
        """
        Create a Role instance from JSON data.

        Args:
            data: Dictionary containing role data from the API

        Returns:
            Role instance with the data
        """
        return cls(
            date_created=data.get("dateCreated", []),
            date_modified=data.get("dateModified", []),
            role_id=data.get("roleId", ""),
            community_id=data.get("communityId", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            level=data.get("level", 0),
            type=data.get("type", ""),
            inactive=data.get("inactive", False),
        )


@dataclass
class User:
    user_id: str
    login: str
    first_name: str
    last_name: str
    email: str
    user_active_in_study: bool
    roles: List[Role]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "User":
        """
        Create a User instance from JSON data.

        Args:
            data: Dictionary containing user data from the API

        Returns:
            User instance with the data
        """
        # Handle nested roles
        roles = []
        roles_data = data.get("roles", [])
        for role_data in roles_data:
            roles.append(Role.from_json(role_data))

        return cls(
            user_id=data.get("userId", ""),
            login=data.get("login", ""),
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
            user_active_in_study=data.get("userActiveInStudy", False),
            roles=roles,
        )
