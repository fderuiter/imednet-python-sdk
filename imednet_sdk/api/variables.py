# API client for interacting with iMednet Variables endpoints.

from typing import List

from ..models._common import ApiResponse
from ..models.variable import VariableModel
from ._base import ResourceClient


class VariablesClient(ResourceClient):
    """Client for managing variables within a study."""

    def list_variables(self, study_key: str, **kwargs) -> ApiResponse[List[VariableModel]]:
        """Lists variables for a specific study.

        Args:
            study_key (str): The key identifying the study.
            **kwargs: Optional keyword arguments for pagination, sorting, filtering, etc.
                      (e.g., page, size, sort, filter).

        Returns:
            ApiResponse[List[VariableModel]]: An API response object containing a list
                                              of variables and metadata.

        Raises:
            ValueError: If study_key is not provided.
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/variables"
        return self._client._get(
            endpoint, params=kwargs, response_model=ApiResponse[List[VariableModel]]
        )
