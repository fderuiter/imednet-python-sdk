# API client for interacting with iMednet Visits endpoints.

from typing import List

from ..models._common import ApiResponse
from ..models.visit import VisitModel
from ._base import ResourceClient


class VisitsClient(ResourceClient):
    """Client for managing visits within a study."""

    def list_visits(self, study_key: str, **kwargs) -> ApiResponse[List[VisitModel]]:
        """Lists visits for a specific study.

        Args:
            study_key (str): The key identifying the study.
            **kwargs: Optional keyword arguments for pagination, sorting, filtering, etc.
                      (e.g., page, size, sort, filter).

        Returns:
            ApiResponse[List[VisitModel]]: An API response object containing a list
                                           of visits and metadata.

        Raises:
            ValueError: If study_key is not provided.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")  # Match test expectation

        endpoint = f"/api/v1/edc/studies/{study_key}/visits"
        return self._client._get(
            endpoint, params=kwargs, response_model=ApiResponse[List[VisitModel]]
        )
