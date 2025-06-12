"""Endpoint for managing variables (data points on eCRFs) in a study."""

from typing import Any, Dict, List, Optional

from imednet.core.async_client import AsyncClient
from imednet.core.client import Client
from imednet.core.context import Context
from imednet.core.paginator import Paginator
from imednet.endpoints.base import BaseEndpoint
from imednet.models.variables import Variable
from imednet.utils.filters import build_filter_string


class VariablesEndpoint(BaseEndpoint):
    """
    API endpoint for interacting with variables (data points on eCRFs) in an iMedNet study.

    Provides methods to list and retrieve individual variables.
    """

    path = "/api/v1/edc/studies"

    def __init__(
        self,
        client: Client,
        ctx: Context,
        async_client: AsyncClient | None = None,
    ) -> None:
        super().__init__(client, ctx, async_client)
        self._variables_cache: Dict[str, List[Variable]] = {}

    def list(
        self, study_key: Optional[str] = None, refresh: bool = False, **filters
    ) -> List[Variable]:
        """
        List variables in a study with optional filtering.

        Args:
            study_key: Study identifier (uses default from context if not specified)
            **filters: Additional filter parameters

        Returns:
            List of Variable objects
        """
        filters = self._auto_filter(filters)
        if study_key:
            filters["studyKey"] = study_key

        study = filters.pop("studyKey")
        if not study:
            raise ValueError("Study key must be provided or set in the context")
        if not filters and not refresh and study in self._variables_cache:
            return self._variables_cache[study]

        params: Dict[str, Any] = {}
        if filters:
            params["filter"] = build_filter_string(filters)

        path = self._build_path(study, "variables")
        paginator = Paginator(self._client, path, params=params, page_size=500)
        result = [Variable.from_json(item) for item in paginator]
        if not filters:
            self._variables_cache[study] = result
        return result

    def get(self, study_key: str, variable_id: int) -> Variable:
        """
        Get a specific variable by ID.

        Args:
            study_key: Study identifier
            variable_id: Variable identifier

        Returns:
            Variable object
        """
        path = self._build_path(study_key, "variables", variable_id)
        raw = self._client.get(path).json().get("data", [])
        if not raw:
            raise ValueError(f"Variable {variable_id} not found in study {study_key}")
        return Variable.from_json(raw[0])
