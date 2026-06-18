"""Endpoint for managing queries (dialogue/questions) in a study."""

from imednet.core.endpoint.edc_mixin import EdcAsyncListGetEndpoint, EdcSyncListGetEndpoint
from imednet.core.endpoint.strategies import PopStudyKeyStrategy
from imednet.models.queries import Query


class QueriesOperationDef:
    PATH = "queries"
    MODEL = Query
    _id_param = "annotationId"
    STUDY_KEY_STRATEGY = PopStudyKeyStrategy()


class QueriesEndpoint(QueriesOperationDef, EdcSyncListGetEndpoint[Query]):  # type: ignore[misc]
    pass


class AsyncQueriesEndpoint(QueriesOperationDef, EdcAsyncListGetEndpoint[Query]):  # type: ignore[misc]
    pass
