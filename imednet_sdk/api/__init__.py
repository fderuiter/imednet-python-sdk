"""
imednet_sdk.api: Resource‑Specific API Clients and Models.

This subpackage contains both:
- Client classes for interacting with specific iMednet API resources.
- Pydantic models representing the data structures those endpoints return.
"""

# Base client and common response models
from ._base import (
    ApiResponse,
    ErrorDetail,
    FieldError,
    Metadata,
    PaginationInfo,
    ResourceClient,
    SortInfo,
)

# Pydantic data models
# API client classes
from .codings import CodingModel, CodingsClient
from .forms import FormModel, FormsClient
from .intervals import IntervalFormModel, IntervalModel, IntervalsClient
from .jobs import JobsClient, JobStatusModel
from .queries import QueriesClient, QueryCommentModel, QueryModel
from .record_revisions import RecordRevisionModel, RecordRevisionsClient
from .records import RecordModel, RecordPostItem, RecordsClient
from .sites import SiteModel, SitesClient
from .studies import StudiesClient, StudyModel
from .subjects import KeywordModel, SubjectModel, SubjectsClient
from .users import UserModel, UserRole, UsersClient
from .variables import VariableModel, VariablesClient
from .visits import VisitModel, VisitsClient

__all__ = [
    # Base
    "ResourceClient",
    # Common models
    "ApiResponse",
    "ErrorDetail",
    "FieldError",
    "Metadata",
    "PaginationInfo",
    "SortInfo",
    # API clients
    "StudiesClient",
    "SitesClient",
    "FormsClient",
    "IntervalsClient",
    "RecordsClient",
    "RecordRevisionsClient",
    "VariablesClient",
    "CodingsClient",
    "SubjectsClient",
    "UsersClient",
    "VisitsClient",
    "JobsClient",
    "QueriesClient",
    # Resource models
    "CodingModel",
    "FormModel",
    "IntervalFormModel",
    "IntervalModel",
    "JobStatusModel",
    "QueryCommentModel",
    "QueryModel",
    "RecordModel",
    "RecordPostItem",
    "RecordRevisionModel",
    "SiteModel",
    "StudyModel",
    "KeywordModel",
    "SubjectModel",
    "UserModel",
    "UserRole",
    "VariableModel",
    "VisitModel",
]
