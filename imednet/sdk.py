"""
Public entry-point for the iMednet SDK.

This module provides the ImednetSDK class which:
- Manages configuration and authentication
- Exposes all endpoint functionality through a unified interface
- Provides context management for proper resource cleanup
"""

from __future__ import annotations

from typing import Optional

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

# Import workflow classes
from .workflows.data_extraction import DataExtractionWorkflow
from .workflows.query_management import QueryManagementWorkflow
from .workflows.record_mapper import RecordMapper
from .workflows.record_update import RecordUpdateWorkflow
from .workflows.site_progress import SiteProgressWorkflow
from .workflows.subject_data import SubjectDataWorkflow


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: "ImednetSDK"):
        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)
        self.site_progress = SiteProgressWorkflow(sdk_instance)


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
        api_key: str,
        security_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3,
        backoff_factor: float = 1.0,
    ):
        """
        Initialize the SDK with authentication and configuration.

        Args:
            api_key: iMednet API key.
            security_key: iMednet security key.
            base_url: Base URL for API; uses default if None.
            timeout: Request timeout in seconds.
            retries: Max retry attempts for transient errors.
            backoff_factor: Factor for exponential backoff between retries.
        """
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
