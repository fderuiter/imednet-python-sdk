"""Endpoint for managing studies in the iMedNet system."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.models.studies import Study


class StudiesOperationDef:
    """Definition for Study operations."""

    PATH = ""
    MODEL = Study
    _id_param = "studyKey"
    requires_study_key: bool = False


class StudiesMixin(StudiesOperationDef):
    """Mixin for Studies operations."""

class StudiesEndpoint(StudiesMixin, EdcSyncListGetEndpoint[Study]):  # type: ignore[misc]
    """Synchronous endpoint for managing Studies."""

    pass


class AsyncStudiesEndpoint(StudiesMixin, EdcAsyncListGetEndpoint[Study]):  # type: ignore[misc]
    """Asynchronous endpoint for managing Studies."""

    pass
