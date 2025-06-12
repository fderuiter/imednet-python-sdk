"""Endpoint for managing studies in the iMedNet system."""

from typing import Any, Dict, List, Optional

from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.studies import Study
from imednet.utils.filters import build_filter_string


class StudiesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with studies in the iMedNet system.

    Provides methods to list available studies and retrieve specific studies.
    """

    path = "/api/v1/edc/studies"

    def __init__(self, client: Client, ctx: Context) -> None:
        super().__init__(client, ctx)
        self._studies_cache: Optional[List[Study]] = None

    def list(self, refresh: bool = False, **filters) -> List[Study]:
        """
        List studies with optional filtering.

        Args:
            **filters: Filter parameters

        Returns:
            List of Study objects
        """
        filters = self._auto_filter(filters)
        if not filters and not refresh and self._studies_cache is not None:
            return self._studies_cache

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)
        paginator = Paginator(self._client, self.path, params=params)
        result = [Study.model_validate(item) for item in paginator]
        if not filters:
            self._studies_cache = result
        return result

    def get(self, study_key: str) -> Study:
        """
        Get a specific study by key.

        Args:
            study_key: Study identifier

        Returns:
            Study object
        """
        path = self._build_path(study_key)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Study {study_key} not found")
        return Study.model_validate(raw[0])
