"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Union
from typing import Any, Dict, List, Optional, Union

from .core.client import Client
from .core.context import Context
from .endpoints.codings import CodingsEndpoint
from .endpoints.forms import FormsEndpoint
from .endpoints.intervals import IntervalsEndpoint
from .endpoints.jobs import JobsEndpoint
from .endpoints.queries import QueriesEndpoint
from .endpoints.record_revisions import RecordRevisionsEndpoint
from .endpoints.records import RecordsEndpoint
from .endpoints.sites import SitesEndpoint
from .endpoints.studies import StudiesEndpoint
from .endpoints.subjects import SubjectsEndpoint
from .endpoints.users import UsersEndpoint
from .endpoints.variables import VariablesEndpoint
from .endpoints.visits import VisitsEndpoint
from .models.codings import Coding
from .models.forms import Form
from .models.intervals import Interval
from .models.jobs import Job
from .models.queries import Query
from .models.record_revisions import RecordRevision
from .models.records import Record
from .models.sites import Site
from .models.studies import Study
from .models.subjects import Subject
from .models.users import User
from .models.variables import Variable
from .models.visits import Visit

# Import workflow classes
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.query_management import QueryManagementWorkflow
from .workflows.record_mapper import RecordMapper
from .workflows.record_update import RecordUpdateWorkflow
from .workflows.subject_data import SubjectDataWorkflow


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: "ImednetSDK"):
        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)


class ImednetSDK:
    """
    Public entry-point for library users.

    Provides access to all iMednet API endpoints and maintains configuration.

    Attributes:
        ctx: Context object for storing state across SDK calls.
        studies: Access to study-related endpoints.
        forms: Access to form-related endpoints.
        subjects: Access to subject-related endpoints.
        etc...
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        security_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        """
        Initialize the SDK with authentication and configuration.

        Args:
            api_key: iMednet API key. If not provided, the value from the
                ``IMEDNET_API_KEY`` environment variable will be used.
            security_key: iMednet security key. If not provided, the value from
                the ``IMEDNET_SECURITY_KEY`` environment variable will be used.
            base_url: Base URL for API. Falls back to ``IMEDNET_BASE_URL`` if
                unset and defaults to the production URL otherwise.
            timeout: Request timeout in seconds.
            retries: Max retry attempts for transient errors.
            backoff_factor: Factor for exponential backoff between retries.
        """
        api_key = api_key or os.getenv("IMEDNET_API_KEY")
        security_key = security_key or os.getenv("IMEDNET_SECURITY_KEY")
        if not api_key or not security_key:
            raise ValueError("API key and security key are required")
        base_url = base_url or os.getenv("IMEDNET_BASE_URL")

        # Initialize context for storing state
        self.ctx = Context()

        # Initialize the HTTP client
        self._client = Client(
            api_key=api_key,
            security_key=security_key,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff_factor=backoff_factor,
        )

        # Initialize endpoint clients
        self.codings = CodingsEndpoint(self._client, self.ctx)
        self.forms = FormsEndpoint(self._client, self.ctx)
        self.intervals = IntervalsEndpoint(self._client, self.ctx)
        self.jobs = JobsEndpoint(self._client, self.ctx)
        self.queries = QueriesEndpoint(self._client, self.ctx)
        self.record_revisions = RecordRevisionsEndpoint(self._client, self.ctx)
        self.records = RecordsEndpoint(self._client, self.ctx)
        self.sites = SitesEndpoint(self._client, self.ctx)
        self.studies = StudiesEndpoint(self._client, self.ctx)
        self.subjects = SubjectsEndpoint(self._client, self.ctx)
        self.users = UsersEndpoint(self._client, self.ctx)
        self.variables = VariablesEndpoint(self._client, self.ctx)
        self.visits = VisitsEndpoint(self._client, self.ctx)

        # Initialize workflows, passing the SDK instance itself
        self.workflows = Workflows(self)

    def __enter__(self) -> ImednetSDK:
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources when exiting context."""
        self.close()

    def close(self) -> None:
        """Close the client connection and free resources."""
        self._client.close()

    def set_default_study(self, study_key: str) -> None:
        """
        Set the default study key for subsequent API calls.

        Args:
            study_key: The study key to use as default.
        """
        self.ctx.set_default_study_key(study_key)

    def clear_default_study(self) -> None:
        """Clear the default study key."""
        self.ctx.clear_default_study_key()

    # ------------------------------------------------------------------
    # Convenience wrappers around common endpoint methods
    # ------------------------------------------------------------------

    def get_studies(self, **filters: Any) -> List[Study]:
        """Return all studies accessible by the current API key."""
        return self.studies.list(**filters)

    def get_records(
        self,
        study_key: str,
        record_data_filter: Optional[str] = None,
        **filters: Any,
    ) -> List[Record]:
        """Return records for the specified study."""
        return self.records.list(
            study_key=study_key,
            record_data_filter=record_data_filter,
            **filters,
        )

    def get_sites(self, study_key: str, **filters: Any) -> List[Site]:
        """Return sites for the specified study."""
        return self.sites.list(study_key, **filters)

    def get_subjects(self, study_key: str, **filters: Any) -> List[Subject]:
        """Return subjects for the specified study."""
        return self.subjects.list(study_key, **filters)

    def create_record(
        self,
        study_key: str,
        records_data: List[Dict[str, Any]],
        email_notify: Union[bool, str, None] = None,
    ) -> Job:
        """Create records in the specified study."""
        return self.records.create(
            study_key,
            records_data,
            email_notify=email_notify,
        )

    def get_forms(self, study_key: str, **filters: Any) -> List[Form]:
        """Return forms for the specified study."""
        return self.forms.list(study_key, **filters)

    def get_intervals(self, study_key: str, **filters: Any) -> List[Interval]:
        """Return intervals for the specified study."""
        return self.intervals.list(study_key, **filters)

    def get_variables(self, study_key: str, **filters: Any) -> List[Variable]:
        """Return variables for the specified study."""
        return self.variables.list(study_key, **filters)

    def get_visits(self, study_key: str, **filters: Any) -> List[Visit]:
        """Return visits for the specified study."""
        return self.visits.list(study_key, **filters)

    def get_codings(self, study_key: str, **filters: Any) -> List[Coding]:
        """Return codings for the specified study."""
        return self.codings.list(study_key, **filters)

    def get_queries(self, study_key: str, **filters: Any) -> List[Query]:
        """Return queries for the specified study."""
        return self.queries.list(study_key, **filters)

    def get_record_revisions(self, study_key: str, **filters: Any) -> List[RecordRevision]:
        """Return record revisions for the specified study."""
        return self.record_revisions.list(study_key, **filters)

    def get_users(self, study_key: str, include_inactive: bool = False) -> List[User]:
        """Return users for the specified study."""
        return self.users.list(study_key, include_inactive)

    def get_job(self, study_key: str, batch_id: str) -> Job:
        """Return job details for the specified batch."""
        return self.jobs.get(study_key, batch_id)
