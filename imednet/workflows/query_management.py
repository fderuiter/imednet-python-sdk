"""Provides workflows for managing queries within iMednet studies."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from ..models import Query

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class QueryManagementWorkflow:
    """
    Provides methods for common query management tasks.

    Args:
        sdk: An instance of the ImednetSDK.
    """

    def __init__(self, sdk: "ImednetSDK"):
        self._sdk = sdk

    def get_open_queries(
        self,
        study_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Query]:
        """
        Retrieves all open queries for a given study, potentially filtered further.

        An 'open' query is defined as one where the query comment with the highest
        sequence number has its 'closed' field set to False.

        Note: This method fetches queries based on `additional_filter` and then
        filters for the 'open' state client-side.

        Args:
            study_key: The key identifying the study.
            additional_filter: An optional dictionary of conditions to apply via the API.
            **kwargs: Additional keyword arguments passed directly to `sdk.queries.list`.

        Returns:
            A list of open Query objects matching the criteria.
        """
        filters = dict(additional_filter) if additional_filter else {}

        # Fetch potentially relevant queries
        all_matching_queries = self._sdk.queries.list(study_key, **filters, **kwargs)

        open_queries: List[Query] = []
        for query in all_matching_queries:
            if not query.query_comments:
                # Cannot determine state, assume not open for this purpose
                continue

            # Find the comment with the highest sequence number
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)

            # Check if the latest comment indicates the query is open (closed=False)
            if not latest_comment.closed:
                open_queries.append(query)

        return open_queries

    def get_queries_for_subject(
        self,
        study_key: str,
        subject_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Query]:
        """
        Retrieves all queries for a specific subject within a study.

        Args:
            study_key: The key identifying the study.
            subject_key: The key identifying the subject.
            additional_filter: An optional dictionary of conditions to combine
                with the subject filter.
            **kwargs: Additional keyword arguments passed directly to `sdk.queries.list`.

        Returns:
            A list of Query objects for the specified subject.
        """
        # Build filter dictionary
        final_filter_dict: Dict[str, Any] = {"subject_key": subject_key}
        if additional_filter:
            final_filter_dict.update(additional_filter)

        return self._sdk.queries.list(study_key, **final_filter_dict, **kwargs)

    def get_queries_by_site(
        self,
        study_key: str,
        site_key: str,
        additional_filter: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
        **kwargs: Any,
    ) -> List[Query]:
        """
        Retrieves all queries for a specific site within a study.

        Args:
            study_key: The key identifying the study.
            site_key: The name of the site.
            additional_filter: Extra conditions to combine with the subject filter.
            **kwargs: Additional keyword arguments passed directly to `sdk.queries.list`.

        Returns:
            A list of Query objects for the specified site.
        """
        subjects = self._sdk.subjects.list(study_key, site_name=site_key)
        subject_keys = [s.subject_key for s in subjects]
        if not subject_keys:
            return []

        final_filter_dict: Dict[str, Any] = {"subject_key": subject_keys}
        if additional_filter:
            final_filter_dict.update(additional_filter)

        return self._sdk.queries.list(study_key, **final_filter_dict, **kwargs)

    def get_query_state_counts(self, study_key: str, **kwargs: Any) -> Dict[str, int]:
        """
        Counts queries grouped by their current state (open/closed/unknown).

        The state is determined by the 'closed' field of the query comment
        with the highest sequence number. Queries without any comments are
        counted as 'unknown'.

        Note: This method fetches all queries matching the base criteria (if any
        are passed via kwargs) and then performs the aggregation client-side.

        Args:
            study_key: The key identifying the study.
            **kwargs: Additional keyword arguments passed directly to `sdk.queries.list`
                      (e.g., for initial filtering before counting).

        Returns:
            A dictionary with keys 'open', 'closed', 'unknown' and their respective counts.
        """
        all_queries = self._sdk.queries.list(study_key, **kwargs)
        # Initialize counts for all possible states
        state_counts: Dict[str, int] = {"open": 0, "closed": 0, "unknown": 0}

        for query in all_queries:
            if not query.query_comments:
                state_counts["unknown"] += 1
                continue

            # Find the comment with the highest sequence number
            latest_comment = max(query.query_comments, key=lambda c: c.sequence)

            # Increment count based on the 'closed' status
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
