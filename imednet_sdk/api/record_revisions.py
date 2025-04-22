"""API client for interacting with the iMednet Record Revisions endpoints.

This module provides the `RecordRevisionsClient` class for accessing record revision
history within a specific study via the iMednet API.
"""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.record_revision import RecordRevisionModel

from ._base import ResourceClient


class RecordRevisionsClient(ResourceClient):
    """Provides methods for accessing iMednet record revision history.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/record-revisions`.
    It is accessed via the `imednet_sdk.client.ImednetClient.record_revisions` property.
    """

    def list_record_revisions(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[RecordRevisionModel]]:
        """Retrieves a list of record revisions for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/record-revisions` endpoint.
        Supports standard pagination, filtering, and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: The index of the page to return (0-based). Defaults to 0.
            size: The number of items per page. Defaults to 25, maximum 500.
            sort: The property to sort by, optionally including direction
                  (e.g., 'recordId,asc', 'dateCreated,desc').
            filter: The filter criteria to apply (e.g., 'recordId==123',
                    'subjectId=="S-001"'). Refer to iMednet API docs for syntax.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request.

        Returns:
            An `ApiResponse` object containing a list of `RecordRevisionModel` instances
            representing the record revisions, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/record-revisions"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter

        # Pass any additional kwargs directly to the underlying request method
        params.update(kwargs)

        # Use self._get instead of self._client._get
        response: ApiResponse[List[RecordRevisionModel]] = self._get(
            endpoint, params=params, response_model=ApiResponse[List[RecordRevisionModel]]
        )
        return response
