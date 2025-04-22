"""imednet_sdk.models: Pydantic Data Models

This subpackage contains Pydantic models representing the data structures
used by the iMednet API.

These models are used for:
- Deserializing JSON responses from the API into typed Python objects.
- Serializing Python objects into JSON payloads for API requests (e.g., creating records).
- Providing type hints and validation for API data.

Common models like `ApiResponse` and error details are defined in `_common.py`,
while resource-specific models (e.g., `StudyModel`, `RecordModel`) are in their
respective files.
"""

from ._common import ApiResponse, ErrorDetail, FieldError, Metadata, PaginationInfo, SortInfo
from .coding import CodingModel
from .form import FormModel
from .interval import IntervalFormModel, IntervalModel
from .job import JobStatusModel
from .query import QueryCommentModel, QueryModel
from .record import RecordCreateRequest, RecordModel
from .record_revision import RecordRevisionModel
from .site import SiteModel
from .study import StudyModel
from .subject import KeywordModel, SubjectModel
from .user import UserModel, UserRole
from .variable import VariableModel
from .visit import VisitModel

__all__ = [
    # Common models
    "ApiResponse",
    "ErrorDetail",
    "FieldError",
    "Metadata",
    "PaginationInfo",
    "SortInfo",
    # Resource models
    "CodingModel",
    "FormModel",
    "IntervalFormModel",
    "IntervalModel",
    "JobStatusModel",
    "KeywordModel",
    "QueryCommentModel",
    "QueryModel",
    "RecordCreateRequest",
    "RecordModel",
    "RecordRevisionModel",
    "SiteModel",
    "StudyModel",
    "SubjectModel",
    "UserModel",
    "UserRole",
    "VariableModel",
    "VisitModel",
]
