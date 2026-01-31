"""Workflow helpers built on top of the iMednet SDK."""

from typing import TYPE_CHECKING

from .data_extraction import DataExtractionWorkflow
from .job_poller import JobPoller, JobTimeoutError
from .query_management import QueryManagementWorkflow
from .record_mapper import RecordMapper
from .record_update import RecordUpdateWorkflow
from .register_subjects import RegisterSubjectsWorkflow
from .study_structure import async_get_study_structure, get_study_structure
from .subject_data import SubjectDataWorkflow

if TYPE_CHECKING:
    from ..sdk import ImednetSDK


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: "ImednetSDK"):
        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)


__all__ = [
    "Workflows",
    "DataExtractionWorkflow",
    "QueryManagementWorkflow",
    "RecordMapper",
    "RecordUpdateWorkflow",
    "JobPoller",
    "JobTimeoutError",
    "RegisterSubjectsWorkflow",
    "SubjectDataWorkflow",
    "get_study_structure",
    "async_get_study_structure",
]
