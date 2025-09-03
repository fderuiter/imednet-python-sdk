from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..sdk import ImednetSDK

from .job_poller import JobPoller, JobTimeoutError
from .query_management import QueryManagementWorkflow
from .record_mapper import RecordMapper
from .record_update import RecordUpdateWorkflow
from .register_subjects import RegisterSubjectsWorkflow
from .study_structure import async_get_study_structure, get_study_structure
from .subject_data import SubjectDataWorkflow


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: "ImednetSDK"):
        """Initializes the Workflows namespace.

        Args:
            sdk_instance: An instance of the ImednetSDK.
        """
        from .data_extraction import DataExtractionWorkflow
        from .query_management import QueryManagementWorkflow
        from .record_mapper import RecordMapper
        from .record_update import RecordUpdateWorkflow
        from .subject_data import SubjectDataWorkflow

        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)


__all__ = [
    "Workflows",
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
