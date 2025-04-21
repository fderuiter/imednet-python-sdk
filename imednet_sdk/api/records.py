"""Client for interacting with the Records endpoint."""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.job import JobStatusModel
from imednet_sdk.models.record import RecordModel, RecordPostItem

from ._base import ResourceClient


class RecordsClient(ResourceClient):
    """Client for the Records API resource."""

    def list_records(
        self,
        study_key: str,
        page: Optional[int] = None,
        size: Optional[int] = None,
        sort: Optional[str] = None,
        filter: Optional[str] = None,
        record_data_filter: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[List[RecordModel]]:
        """
        Retrieve a list of records for a specific study.

        Corresponds to `GET /api/v1/edc/studies/{studyKey}/records`.

        Args:
            study_key: The key of the study for which to list records.
            page: Index page to return. Default is 0.
            size: Number of items per page. Default is 25. Max 500.
            sort: Property to sort by (e.g., 'recordId,asc').
            filter: Filter criteria for standard record properties (e.g., 'siteId==123').
            record_data_filter: Filter criteria for data within the recordData field
                                (e.g., 'fieldName=="value"').
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            An ApiResponse containing a list of RecordModel objects.

        Raises:
            ValueError: If study_key is empty or None.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/records"
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if sort is not None:
            params["sort"] = sort
        if filter is not None:
            params["filter"] = filter
        if record_data_filter is not None:
            params["recordDataFilter"] = record_data_filter  # Note the camelCase

        # Pass any additional kwargs directly to the underlying request method
        params.update(kwargs)

        return self._client._get(
            endpoint, params=params, response_model=ApiResponse[List[RecordModel]]
        )

    def create_records(
        self,
        study_key: str,
        records: List[RecordPostItem],
        email_notify: Optional[str] = None,
        **kwargs: Any,
    ) -> ApiResponse[JobStatusModel]:
        """
        Create one or more records within a specific study.

        Corresponds to `POST /api/v1/edc/studies/{studyKey}/records`.

        Args:
            study_key: The key of the study where records will be created.
            records: A list of RecordPostItem objects representing the records to create.
            email_notify: Optional email address to notify upon job completion.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            An ApiResponse containing the JobStatusModel for the background job.

        Raises:
            ValueError: If study_key is empty or None, or if records list is empty.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")
        if not records:
            raise ValueError("records list cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/records"

        # Prepare headers
        headers = {}
        if email_notify:
            headers["x-email-notify"] = email_notify

        # Prepare data - Pydantic handles serialization of the list of models
        # The base client's _request method will handle json serialization

        # Use _post method from the base client
        return self._client._post(
            endpoint,
            json=[
                record.model_dump(exclude_none=True) for record in records
            ],  # Serialize list of models
            headers=headers,
            response_model=ApiResponse[JobStatusModel],
            **kwargs,
        )
