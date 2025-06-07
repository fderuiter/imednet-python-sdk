"""Async endpoint for managing users in a study."""

from typing import List, Optional, Union, cast

from imednet.core.async_client import AsyncClient
from imednet.core.async_paginator import AsyncPaginator
from imednet.endpoints.base import BaseEndpoint
from imednet.endpoints.helpers import build_paginator
from imednet.models.users import User


class AsyncUsersEndpoint(BaseEndpoint[AsyncClient]):
    """Async API endpoint for interacting with study users."""

    path = "/api/v1/edc/studies"

    def __init__(self, client: AsyncClient, ctx, default_page_size: int = 100) -> None:
        super().__init__(client, ctx, default_page_size=default_page_size)

    async def list(
        self,
        study_key: Optional[str] = None,
        include_inactive: bool = False,
        page_size: Optional[int] = None,
    ) -> List[User]:
        study_key = study_key or self._ctx.default_study_key
        if not study_key:
            raise ValueError("Study key must be provided or set in the context")

        paginator = cast(
            AsyncPaginator,
            build_paginator(
                self,
                AsyncPaginator,
                "users",
                study_key,
                page_size,
                None,
                extra_params={"includeInactive": str(include_inactive).lower()},
            ),
        )
        return [User.from_json(item) async for item in paginator]

    async def get(self, study_key: str, user_id: Union[str, int]) -> User:
        path = self._build_path(study_key, "users", user_id)
        response = await self._client.get(path)
        raw = response.json().get("data", [])
        if not raw:
            raise ValueError(f"User {user_id} not found in study {study_key}")
        return User.from_json(raw[0])
