"""API client for interacting with iMednet Codings endpoints."""

from typing import List

from ..models._common import ApiResponse
from ..models.coding import CodingModel
from ._base import ResourceClient


class CodingsClient(ResourceClient):
    """Client for managing codings within a study."""

    def list_codings(self, study_key: str, **kwargs) -> ApiResponse[List[CodingModel]]:
        """Lists codings for a specific study.

        Args:
            study_key (str): The key identifying the study.
            **kwargs: Optional keyword arguments for pagination, sorting, filtering, etc.
                      (e.g., page, size, sort, filter).

        Returns:
            ApiResponse[List[CodingModel]]: An API response object containing a list
                                            of codings and metadata.

        Raises:
            ValueError: If study_key is not provided.
        """
        if not study_key:
            raise ValueError("study_key is required.")

        endpoint = f"/api/v1/edc/studies/{study_key}/codings"
        return self._client._get(
            endpoint, params=kwargs, response_model=ApiResponse[List[CodingModel]]
        )
