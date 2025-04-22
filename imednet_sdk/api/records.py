"""API client for interacting with the iMednet Records endpoints.

This module provides the `RecordsClient` class for accessing and creating
record data within a specific study via the iMednet API.
"""

from typing import Any, Dict, List, Optional

from imednet_sdk.models._common import ApiResponse
from imednet_sdk.models.job import JobStatusModel
from imednet_sdk.models.record import RecordModel, RecordPostItem

from ._base import ResourceClient


class RecordsClient(ResourceClient):
    """Provides methods for accessing and creating iMednet record data.

    This client interacts with endpoints under `/api/v1/edc/studies/{study_key}/records`.
    It is accessed via the `imednet_sdk.client.ImednetClient.records` property.
    """

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
        """Retrieves a list of records for a specific study.

        Corresponds to the `GET /api/v1/edc/studies/{studyKey}/records` endpoint.
        Supports standard pagination, filtering (on record metadata and data),
        and sorting parameters.

        Args:
            study_key: The unique identifier for the study.
            page: The index of the page to return (0-based). Defaults to 0.
            size: The number of items per page. Defaults to 25, maximum 500.
            sort: The property to sort by, optionally including direction
                  (e.g., 'recordId,asc', 'subjectId,desc').
            filter: The filter criteria to apply to standard record properties
                    (e.g., 'siteId==123', 'formKey=="AE"'). Refer to iMednet API
                    docs for syntax.
            record_data_filter: The filter criteria to apply to fields within the
                                `recordData` object (e.g., 'AETERM=="Headache"',
                                'AESEV=="Mild"'). Refer to iMednet API docs for syntax.
            **kwargs: Additional keyword arguments passed directly as query parameters
                      to the API request.

        Returns:
            An `ApiResponse` object containing a list of `RecordModel` instances
            representing the records, along with pagination/metadata details.

        Raises:
            ValueError: If `study_key` is empty or not provided.
            ImednetSdkException: If the API request fails (e.g., network error,
                               authentication issue, invalid permissions).
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

        # Use self._get instead of self._client._get
        return self._get(endpoint, params=params, response_model=ApiResponse[List[RecordModel]])

    def create_records(
        self,
        study_key: str,
        records: List[RecordPostItem],
        email_notify: Optional[str] = None,
        **kwargs: Any,
    ) -> JobStatusModel:
        """Creates one or more records within a specific study asynchronously.

        Corresponds to the `POST /api/v1/edc/studies/{studyKey}/records` endpoint.
        This operation initiates a background job in iMednet.

        Args:
            study_key: The unique identifier for the study where the records
                       will be created.
            records: A list of `RecordPostItem` objects, each defining a record
                     to be created. Each item must include required fields like
                     `formKey`, `subjectId`, `siteId`, `intervalName`, `visitName`,
                     and the `recordData` dictionary.
            email_notify: An optional email address to which iMednet will send a
                          notification upon completion of the background job.
            **kwargs: Additional keyword arguments passed directly to the underlying
                      request method (e.g., custom headers, timeout).

        Returns:
            A `JobStatusModel` instance containing the `batchId` and initial status
            of the background job created to process the record creation request.
            Use the `JobsClient.get_job_status` method with the `batchId` to track
            the job's progress.

        Raises:
            ValueError: If `study_key` is empty or not provided, or if the `records`
                        list is empty.
            ImednetSdkException: If the API request fails to initiate the job (e.g.,
                               network error, authentication issue, invalid input format).
                               Note that errors during the background job processing itself
                               will be reflected in the job status, not raised here.
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
        records_payload = [record.model_dump(exclude_none=True) for record in records]

        # Use self._post instead of self._client._post
        return self._post(
            endpoint,
            json=records_payload,
            headers=headers,
            response_model=JobStatusModel,  # Expect JobStatusModel directly
        )
