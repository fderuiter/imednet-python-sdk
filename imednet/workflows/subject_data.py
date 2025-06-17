"""Provides a workflow to retrieve comprehensive data for a specific subject."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..models import Query, Record, Subject, Visit

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


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

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    def get_all_subject_data(self, study_key: str, subject_key: str) -> SubjectComprehensiveData:
        """
        Retrieves subject details, visits, records, and queries for a specific subject.

        Args:
            study_key: The key identifying the study.
            subject_key: The key identifying the subject.

        Returns:
            A SubjectComprehensiveData object containing the aggregated data.
        """
        results = SubjectComprehensiveData(subject_details=None)
        subject_filter_dict: Dict[str, Any] = {"subject_key": subject_key}

        # Fetch Subject Details
        subject_list = self._sdk.subjects.list(study_key, **subject_filter_dict)
        if subject_list:
            results.subject_details = subject_list[0]

        # Fetch Visits
        results.visits = self._sdk.visits.list(study_key, **subject_filter_dict)

        # Fetch Records
        results.records = self._sdk.records.list(study_key, **subject_filter_dict)

        # Fetch Queries
        results.queries = self._sdk.queries.list(study_key, **subject_filter_dict)

        return results


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.subject_data.get_all_subject_data(...)`).
# - Simplifies common tasks by abstracting away the need to call multiple individual endpoints.
