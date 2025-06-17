"""Provides workflows for extracting specific datasets from iMednet studies."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ..models import Record, RecordRevision

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class DataExtractionWorkflow:
    """
    Provides methods for complex data extraction tasks involving multiple iMednet endpoints.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    def extract_records_by_criteria(
        self,
        study_key: str,
        record_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        subject_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        visit_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **other_filters: Any,
    ) -> List[Record]:
        """
        Extracts records based on criteria spanning subjects, visits, and records.

        Args:
            study_key: The key identifying the study.
            record_filter: Dictionary of conditions for the records endpoint.
            subject_filter: Dictionary of conditions for the subjects endpoint.
            visit_filter: Dictionary of conditions for the visits endpoint.
            **other_filters: Additional keyword arguments passed as filters to the
                             records endpoint `list` method.

        Returns:
            A list of Record objects matching all specified criteria.
        """
        matching_subject_keys: Optional[List[str]] = None
        if subject_filter:
            subjects = self._sdk.subjects.list(study_key, **subject_filter)
            matching_subject_keys = [s.subject_key for s in subjects]
            if not matching_subject_keys:
                return []

        # Changed type hint from List[str] to List[int]
        matching_visit_ids: Optional[List[int]] = None
        if visit_filter:
            # Client-side filtering for subject_key on visits is still needed
            # as build_filter_string doesn't handle complex AND/OR structures easily
            # from separate filter dictionaries.
            visits = self._sdk.visits.list(study_key, **visit_filter)

            if matching_subject_keys:
                visits = [v for v in visits if v.subject_key in matching_subject_keys]

            # Corrected attribute from oid to visit_id
            matching_visit_ids = [v.visit_id for v in visits]
            if not matching_visit_ids:
                return []

        # Build the final record filter dictionary
        final_record_filter_dict = dict(record_filter) if record_filter else {}
        final_record_filter_dict.update(other_filters)  # Add other_filters here

        # Client-side filtering is used below for subject/visit matching,
        # so no need to add complex 'in' clauses here even if build_filter_string supported it.

        records = self._sdk.records.list(
            study_key=study_key,
            record_data_filter=None,
            **final_record_filter_dict,
        )

        # Client-side filtering fallback
        if matching_subject_keys:
            records = [r for r in records if r.subject_key in matching_subject_keys]
        # Corrected attribute from visit_oid to visit_id and variable name
        if matching_visit_ids:
            records = [r for r in records if r.visit_id in matching_visit_ids]

        return records

    def extract_audit_trail(
        self,
        study_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **filters: Any,
    ) -> List[RecordRevision]:
        """
        Extracts the audit trail (record revisions) based on specified filters.

        Args:
            study_key: The key identifying the study.
            start_date: Optional start date filter (YYYY-MM-DD format expected by API).
            end_date: Optional end date filter (YYYY-MM-DD format expected by API).
            user_filter: Optional dictionary of base filter conditions.
            **filters: Additional key-value pairs to be added as equality filters.

        Returns:
            A list of RecordRevision objects matching the criteria.
        """
        # Start with the user_filter dict if provided, otherwise an empty dict
        final_filter_dict = dict(user_filter) if user_filter else {}

        # Add additional filters from kwargs
        final_filter_dict.update(filters)

        # Prepare keyword arguments for date filters if they exist
        date_kwargs = {}
        if start_date:
            date_kwargs["start_date"] = start_date
        if end_date:
            date_kwargs["end_date"] = end_date

        # Fetch record revisions
        revisions = self._sdk.record_revisions.list(
            study_key,
            **final_filter_dict,
            **date_kwargs,
        )
        return revisions


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.data_extraction.extract_records_by_criteria(...)`).
# - Offers powerful data retrieval capabilities beyond single endpoint calls.
