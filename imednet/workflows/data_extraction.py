"""Provides workflows for extracting specific datasets from iMednet studies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ..models import Record, RecordRevision

if TYPE_CHECKING:
    from ..sdk import AsyncImednetSDK, ImednetSDK


class DataExtractionWorkflow:
    """
    Provides methods for complex data extraction tasks involving multiple iMednet endpoints.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK | AsyncImednetSDK"):
        from ..sdk import AsyncImednetSDK

        self._sdk = sdk
        self._is_async = isinstance(sdk, AsyncImednetSDK)

    def extract_records_by_criteria(
        self,
        study_key: str,
        record_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        subject_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        visit_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **other_filters: Any,
    ) -> Any:
        """Extract records based on subject, visit and record filters."""
        if self._is_async:
            return self._extract_records_by_criteria_async(
                study_key,
                record_filter,
                subject_filter,
                visit_filter,
                **other_filters,
            )
        return self._extract_records_by_criteria_sync(
            study_key,
            record_filter,
            subject_filter,
            visit_filter,
            **other_filters,
        )

    def _extract_records_by_criteria_sync(
        self,
        study_key: str,
        record_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        subject_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        visit_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **other_filters: Any,
    ) -> List[Record]:
        """Synchronous implementation for :meth:`extract_records_by_criteria`."""
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

    async def _extract_records_by_criteria_async(
        self,
        study_key: str,
        record_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        subject_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        visit_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **other_filters: Any,
    ) -> List[Record]:
        """Asynchronous implementation for :meth:`extract_records_by_criteria`."""
        matching_subject_keys: Optional[List[str]] = None
        if subject_filter:
            subjects = await self._sdk.subjects.async_list(study_key, **subject_filter)
            matching_subject_keys = [s.subject_key for s in subjects]
            if not matching_subject_keys:
                return []

        matching_visit_ids: Optional[List[int]] = None
        if visit_filter:
            visits = await self._sdk.visits.async_list(study_key, **visit_filter)
            if matching_subject_keys:
                visits = [v for v in visits if v.subject_key in matching_subject_keys]
            matching_visit_ids = [v.visit_id for v in visits]
            if not matching_visit_ids:
                return []

        final_record_filter_dict = dict(record_filter) if record_filter else {}
        final_record_filter_dict.update(other_filters)

        records = await self._sdk.records.async_list(
            study_key=study_key,
            record_data_filter=None,
            **final_record_filter_dict,
        )

        if matching_subject_keys:
            records = [r for r in records if r.subject_key in matching_subject_keys]
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
    ) -> Any:
        """Extract audit trail entries matching the provided filters."""
        if self._is_async:
            return self._extract_audit_trail_async(
                study_key,
                start_date=start_date,
                end_date=end_date,
                user_filter=user_filter,
                **filters,
            )
        return self._extract_audit_trail_sync(
            study_key,
            start_date=start_date,
            end_date=end_date,
            user_filter=user_filter,
            **filters,
        )

    def _extract_audit_trail_sync(
        self,
        study_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **filters: Any,
    ) -> List[RecordRevision]:
        """Synchronous implementation for :meth:`extract_audit_trail`."""
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

    async def _extract_audit_trail_async(
        self,
        study_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **filters: Any,
    ) -> List[RecordRevision]:
        """Asynchronous implementation for :meth:`extract_audit_trail`."""
        final_filter_dict = dict(user_filter) if user_filter else {}
        final_filter_dict.update(filters)

        date_kwargs = {}
        if start_date:
            date_kwargs["start_date"] = start_date
        if end_date:
            date_kwargs["end_date"] = end_date

        revisions = await self._sdk.record_revisions.async_list(
            study_key,
            **final_filter_dict,
            **date_kwargs,
        )
        return revisions


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.data_extraction.extract_records_by_criteria(...)`).
# - Offers powerful data retrieval capabilities beyond single endpoint calls.
