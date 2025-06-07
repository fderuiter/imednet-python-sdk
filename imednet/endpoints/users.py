"""Endpoint for managing users in a study."""

from typing import List, Optional, Union, cast

from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.users import User


class UsersEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with users in an iMedNet study.

    Provides methods to list and retrieve user information.
    """

    path = "/api/v1/edc/studies"

    def list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        page_size: Optional[int] = None,
    ) -> List[User]:
        """
        List users in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            include_inactive: Whether to include inactive users

        Returns:
            List of User objects
        """
        study_key = study_key or self._ctx.default_study_key
        if not study_key:
            raise ValueError("Study key must be provided or set in the context")

        paginator = cast(
            Paginator,
            build_paginator(
                self,
                Paginator,
                "users",
                study_key,
                page_size,
                None,
                extra_params={"includeInactive": str(include_inactive).lower()},
            ),
        )
        return [User.from_json(item) for item in paginator]

    def get(self, study_key: str, user_id: Union[str, int]) -> User:
        """
        Get a specific user by ID.

        Args:
            study_key: Study identifier
            user_id: User identifier (can be a string UUID or integer ID)

        Returns:
            User object
        """
        path = self._build_path(study_key, "users", user_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"User {user_id} not found in study {study_key}")
        return User.from_json(raw[0])
