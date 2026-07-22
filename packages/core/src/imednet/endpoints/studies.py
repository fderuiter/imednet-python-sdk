"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.studies import Study


class StudiesOperationDef:
    """Definition for Study operations."""

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    requires_study_key: bool = False


class StudiesEndpoint(StudiesOperationDef, EdcSyncListGetEndpoint[Study]):  # type: ignore[misc]
    """Synchronous endpoint for managing Studies."""


class AsyncStudiesEndpoint(StudiesOperationDef, EdcAsyncListGetEndpoint[Study]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Studies."""
