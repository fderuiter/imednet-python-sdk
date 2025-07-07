"""Provides workflows for managing queries within iMednet studies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ..models import Query

if TYPE_CHECKING:
    from ..sdk import AsyncImednetSDK, ImednetSDK


class QueryManagementWorkflow:
    """
    Provides methods for common query management tasks.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK | AsyncImednetSDK"):
        from ..sdk import AsyncImednetSDK

        self._sdk = sdk
        self._is_async = isinstance(sdk, AsyncImednetSDK)

    def get_open_queries(
        self,
        study_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        """Return open queries for a study."""
        if self._is_async:
            return self._get_open_queries_async(study_key, additional_filter, **kwargs)
        return self._get_open_queries_sync(study_key, additional_filter, **kwargs)

    def _get_open_queries_sync(
        self,
        study_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        filters = dict(additional_filter) if additional_filter else {}
        all_matching_queries = self._sdk.queries.list(study_key, **filters, **kwargs)
        open_queries: List[Query] = []
        for query in all_matching_queries:
            if not query.query_comments:
                continue
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)
            if not latest_comment.closed:
                open_queries.append(query)
        return open_queries

    async def _get_open_queries_async(
        self,
        study_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        filters = dict(additional_filter) if additional_filter else {}
        all_matching_queries = await self._sdk.queries.async_list(study_key, **filters, **kwargs)
        open_queries: List[Query] = []
        for query in all_matching_queries:
            if not query.query_comments:
                continue
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)
            if not latest_comment.closed:
                open_queries.append(query)
        return open_queries

    def get_queries_for_subject(
        self,
        study_key: str,
        subject_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        """Return queries for a specific subject."""
        if self._is_async:
            return self._get_queries_for_subject_async(
                study_key,
                subject_key,
                additional_filter,
                **kwargs,
            )
        return self._get_queries_for_subject_sync(
            study_key,
            subject_key,
            additional_filter,
            **kwargs,
        )

    def _get_queries_for_subject_sync(
        self,
        study_key: str,
        subject_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        final_filter_dict: Dict[str, Any] = {"subject_key": subject_key}
        if additional_filter:
            final_filter_dict.update(additional_filter)
        return self._sdk.queries.list(study_key, **final_filter_dict, **kwargs)

    async def _get_queries_for_subject_async(
        self,
        study_key: str,
        subject_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        final_filter_dict: Dict[str, Any] = {"subject_key": subject_key}
        if additional_filter:
            final_filter_dict.update(additional_filter)
        return await self._sdk.queries.async_list(study_key, **final_filter_dict, **kwargs)

    def get_queries_by_site(
        self,
        study_key: str,
        site_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> Any:
        """Return queries for all subjects at a site."""
        if self._is_async:
            return self._get_queries_by_site_async(
                study_key,
                site_key,
                additional_filter,
                **kwargs,
            )
        return self._get_queries_by_site_sync(
            study_key,
            site_key,
            additional_filter,
            **kwargs,
        )

    def _get_queries_by_site_sync(
        self,
        study_key: str,
        site_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Query]:
        subjects = self._sdk.subjects.list(study_key, site_name=site_key)
        subject_keys = [s.subject_key for s in subjects]
        if not subject_keys:
            return []
        final_filter_dict: Dict[str, Any] = {"subject_key": subject_keys}
        if additional_filter:
            final_filter_dict.update(additional_filter)
        return self._sdk.queries.list(study_key, **final_filter_dict, **kwargs)

    async def _get_queries_by_site_async(
        self,
        study_key: str,
        site_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Query]:
        subjects = await self._sdk.subjects.async_list(study_key, site_name=site_key)
        subject_keys = [s.subject_key for s in subjects]
        if not subject_keys:
            return []
        final_filter_dict: Dict[str, Any] = {"subject_key": subject_keys}
        if additional_filter:
            final_filter_dict.update(additional_filter)
        return await self._sdk.queries.async_list(study_key, **final_filter_dict, **kwargs)

    def get_query_state_counts(self, study_key: str, **kwargs: Any) -> Any:
        """Return counts of queries grouped by state."""
        if self._is_async:
            return self._get_query_state_counts_async(study_key, **kwargs)
        return self._get_query_state_counts_sync(study_key, **kwargs)

    def _get_query_state_counts_sync(self, study_key: str, **kwargs: Any) -> Dict[str, int]:
        all_queries = self._sdk.queries.list(study_key, **kwargs)
        state_counts: Dict[str, int] = {"open": 0, "closed": 0, "unknown": 0}
        for query in all_queries:
            if not query.query_comments:
                state_counts["unknown"] += 1
                continue
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)
            if latest_comment.closed:
                state_counts["closed"] += 1
            else:
                state_counts["open"] += 1
        return state_counts

    async def _get_query_state_counts_async(self, study_key: str, **kwargs: Any) -> Dict[str, int]:
        all_queries = await self._sdk.queries.async_list(study_key, **kwargs)
        state_counts: Dict[str, int] = {"open": 0, "closed": 0, "unknown": 0}
        for query in all_queries:
            if not query.query_comments:
                state_counts["unknown"] += 1
                continue
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)
            if latest_comment.closed:
                state_counts["closed"] += 1
            else:
                state_counts["open"] += 1
        return state_counts


# Integration:
# - Accessed via the main SDK instance
#       (e.g., `sdk.workflows.query_management.get_open_queries(...)`).
# - Provides convenient ways to access query information without manually constructing
#   complex filters.
