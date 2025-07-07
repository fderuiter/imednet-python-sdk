"""Provides a workflow to retrieve comprehensive data for a specific subject."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..models import Query, Record, Subject, Visit

if TYPE_CHECKING:
    from ..sdk import AsyncImednetSDK, ImednetSDK


class SubjectComprehensiveData(BaseModel):
    """Structure to hold aggregated data for a subject."""

    subject_details: Optional[Subject] = Field(None, description="Core details of the subject.")
    visits: List[Visit] = Field(default_factory=list, description="List of visits for the subject.")
    records: List[Record] = Field(
        default_factory=list, description="List of records for the subject."
    )
    queries: List[Query] = Field(
        default_factory=list, description="List of queries related to the subject."
    )


class SubjectDataWorkflow:
    """
    Provides methods to retrieve comprehensive data related to a specific subject.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK | AsyncImednetSDK"):
        from ..sdk import AsyncImednetSDK

        self._sdk = sdk
        self._is_async = isinstance(sdk, AsyncImednetSDK)

    def get_all_subject_data(self, study_key: str, subject_key: str) -> Any:
        """Retrieve subject details, visits, records and queries."""
        if self._is_async:
            return self._get_all_subject_data_async(study_key, subject_key)
        return self._get_all_subject_data_sync(study_key, subject_key)

    def _get_all_subject_data_sync(
        self, study_key: str, subject_key: str
    ) -> SubjectComprehensiveData:
        results = SubjectComprehensiveData(subject_details=None)
        subject_filter_dict: Dict[str, Any] = {"subject_key": subject_key}

        subject_list = self._sdk.subjects.list(study_key, **subject_filter_dict)
        if subject_list:
            results.subject_details = subject_list[0]

        results.visits = self._sdk.visits.list(study_key, **subject_filter_dict)
        results.records = self._sdk.records.list(study_key, **subject_filter_dict)
        results.queries = self._sdk.queries.list(study_key, **subject_filter_dict)
        return results

    async def _get_all_subject_data_async(
        self, study_key: str, subject_key: str
    ) -> SubjectComprehensiveData:
        results = SubjectComprehensiveData(subject_details=None)
        subject_filter_dict: Dict[str, Any] = {"subject_key": subject_key}

        subject_list = await self._sdk.subjects.async_list(study_key, **subject_filter_dict)
        if subject_list:
            results.subject_details = subject_list[0]

        results.visits = await self._sdk.visits.async_list(study_key, **subject_filter_dict)
        results.records = await self._sdk.records.async_list(study_key, **subject_filter_dict)
        results.queries = await self._sdk.queries.async_list(study_key, **subject_filter_dict)
        return results


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.subject_data.get_all_subject_data(...)`).
# - Simplifies common tasks by abstracting away the need to call multiple individual endpoints.
