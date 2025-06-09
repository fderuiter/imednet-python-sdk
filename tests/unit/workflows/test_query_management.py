from unittest.mock import MagicMock

from imednet.models.queries import Query, QueryComment
from imednet.workflows.query_management import QueryManagementWorkflow


def test_get_open_queries_omits_none_filter() -> None:
    sdk = MagicMock()
    query = Query.model_validate(
        {
            "annotationId": 1,
            "queryComments": [QueryComment.model_validate({"sequence": 1, "closed": False})],
        }
    )
    sdk.queries.list.return_value = [query]

    wf = QueryManagementWorkflow(sdk)
    result = wf.get_open_queries("STUDY")

    assert result == [query]
    sdk.queries.list.assert_called_once_with("STUDY")
