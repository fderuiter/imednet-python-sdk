"""Namespace for accessing workflow classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from imednet.sdk import ImednetSDK

    from .data_extraction import DataExtractionWorkflow
    from .query_management import QueryManagementWorkflow
    from .record_mapper import RecordMapper
    from .record_update import RecordUpdateWorkflow
    from .subject_data import SubjectDataWorkflow


class Workflows:
    """Namespace for accessing workflow classes."""

    def __init__(self, sdk_instance: ImednetSDK):
        self._sdk = sdk_instance
        self._data_extraction: Optional[DataExtractionWorkflow] = None
        self._query_management: Optional[QueryManagementWorkflow] = None
        self._record_mapper: Optional[RecordMapper] = None
        self._record_update: Optional[RecordUpdateWorkflow] = None
        self._subject_data: Optional[SubjectDataWorkflow] = None

    @property
    def data_extraction(self) -> DataExtractionWorkflow:
        """Access the Data Extraction workflow."""
        if self._data_extraction is None:
            from .data_extraction import DataExtractionWorkflow

            self._data_extraction = DataExtractionWorkflow(self._sdk)
        return self._data_extraction

    @property
    def query_management(self) -> QueryManagementWorkflow:
        """Access the Query Management workflow."""
        if self._query_management is None:
            from .query_management import QueryManagementWorkflow

            self._query_management = QueryManagementWorkflow(self._sdk)
        return self._query_management

    @property
    def record_mapper(self) -> RecordMapper:
        """Access the Record Mapper workflow."""
        if self._record_mapper is None:
            from .record_mapper import RecordMapper

            self._record_mapper = RecordMapper(self._sdk)
        return self._record_mapper

    @property
    def record_update(self) -> RecordUpdateWorkflow:
        """Access the Record Update workflow."""
        if self._record_update is None:
            from .record_update import RecordUpdateWorkflow

            self._record_update = RecordUpdateWorkflow(self._sdk)
        return self._record_update

    @property
    def subject_data(self) -> SubjectDataWorkflow:
        """Access the Subject Data workflow."""
        if self._subject_data is None:
            from .subject_data import SubjectDataWorkflow

            self._subject_data = SubjectDataWorkflow(self._sdk)
        return self._subject_data
