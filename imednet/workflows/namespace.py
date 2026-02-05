"""Namespace for accessing workflow classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .data_extraction import DataExtractionWorkflow
from .query_management import QueryManagementWorkflow
from .record_mapper import RecordMapper
from .record_update import RecordUpdateWorkflow
from .subject_data import SubjectDataWorkflow

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: ImednetSDK):
        self.data_extraction = DataExtractionWorkflow(sdk_instance)
        self.query_management = QueryManagementWorkflow(sdk_instance)
        self.record_mapper = RecordMapper(sdk_instance)
        self.record_update = RecordUpdateWorkflow(sdk_instance)
        self.subject_data = SubjectDataWorkflow(sdk_instance)
