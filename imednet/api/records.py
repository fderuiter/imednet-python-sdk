"""
Pydantic models and API client for iMednet "records".

This module provides:

- `KeywordModel`, `RecordModel`, and `RecordPostItem`: Pydantic models for record data.
- `RecordsClient`: an API client for `/api/v1/edc/studies/{study_key}/records` endpoints.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ._base import ApiResponse, ResourceClient
from .jobs import JobStatusModel

logger = logging.getLogger(__name__)


class KeywordModel(BaseModel):
    """Represents a keyword associated with a record in iMednet."""

    keywordName: str = Field(..., description="Name of the keyword")
    keywordKey: str = Field(..., description="Key of the keyword")
    keywordId: int = Field(..., description="Unique ID of the keyword")
    dateAdded: datetime = Field(..., description="Date the keyword was added")


# Define the base RecordModel here instead of importing it from itself
class RecordModel(BaseModel):
    """Represents a record in iMednet with its metadata."""

    # Add all necessary fields here - this is a placeholder implementation
    # You'll need to add the actual fields based on your data model
    id: Optional[str] = Field(None, description="Unique identifier for the record")
    formKey: Optional[str] = Field(None, description="Form key for this record")
    dateCreated: Optional[datetime] = Field(None, description="Date when the record was created")
    dateModified: Optional[datetime] = Field(
        None, description="Date when the record was last modified"
    )
    # Add other fields as needed

    model_config = ConfigDict(extra="allow")

    @field_validator("dateCreated", "dateModified", mode="before")
    @classmethod
    def _parse_datetime_optional(cls, value):
        """Parse datetime strings into datetime objects, handling None."""
        if value is None or isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            try:
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                logger.warning(f"Could not parse datetime field {value!r}: {e}")
                raise ValueError(f"Invalid datetime format: {value}") from e


# Define the base RecordPostItem here instead of importing it from itself
class RecordPostItem(BaseModel):
    """Represents data needed to create a new record in iMednet."""

    # Add all necessary fields here - this is a placeholder implementation
    # You'll need to add the actual fields based on your data model
    formKey: str = Field(..., description="Form key for this record")
    subjectKey: str = Field(..., description="Subject key for this record")
    # Add other required fields

    # Optional fields
    visitKey: Optional[str] = Field(None, description="Visit key if applicable")
    intervalKey: Optional[str] = Field(None, description="Interval key if applicable")
    # Add other optional fields as needed


class RecordsClient(ResourceClient):
    """Provides methods for accessing and managing iMednet record data."""

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

        GET /api/v1/edc/studies/{studyKey}/records
        Supports pagination, metadata filtering, sorting, and recordDataFilter.

        Args:
            study_key: Unique identifier for the study.
            page: Zero-based page index.
            size: Number of items per page.
            sort: Sort expression (e.g., 'dateCreated,desc').
            filter: Metadata filter (e.g., 'formKey=="AE"').
            record_data_filter: Filter on form field values.
            **kwargs: Additional query parameters.

        Raises:
            ValueError: If `study_key` is empty.
            ImednetSdkException: On API errors.
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
            params["recordDataFilter"] = record_data_filter
        params.update(kwargs)

        # Cast the result to the expected type
        return cast(
            ApiResponse[List[RecordModel]],
            self._get(
                endpoint,
                params=params,
                response_model=ApiResponse[List[RecordModel]],
            ),
        )

    def create_records(
        self,
        study_key: str,
        records: List[RecordPostItem],
        email_notify: Optional[str] = None,
        **kwargs: Any,
    ) -> JobStatusModel:
        """Creates one or more records asynchronously in a background job.

        POST /api/v1/edc/studies/{studyKey}/records

        Args:
            study_key: Unique identifier for the study.
            records: List of RecordPostItem defining records to create.
            email_notify: Optional email for job completion notification.
            **kwargs: Additional request kwargs (headers, timeout, etc.).

        Raises:
            ValueError: If `study_key` is empty or `records` is empty.
            ImednetSdkException: If the request fails to start the job.
        """
        if not study_key:
            raise ValueError("study_key cannot be empty")
        if not records:
            raise ValueError("records list cannot be empty")

        endpoint = f"/api/v1/edc/studies/{study_key}/records"
        headers = {}
        if email_notify:
            headers["x-email-notify"] = email_notify

        payload = [r.model_dump(exclude_none=True) for r in records]
        # Cast the result to the expected type
        return cast(
            JobStatusModel,
            self._post(
                endpoint,
                json=payload,
                # Use the renamed parameter json_payload
                # if _post was also updated, otherwise keep json
                headers=headers,
                response_model=JobStatusModel,
            ),
        )
