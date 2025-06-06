from unittest.mock import MagicMock, patch

from imednet.models.codings import Coding
from imednet.workflows.coding_review import CodingReviewWorkflow


def _make_coding(coding_id: int, variable: str, value: str, code: str) -> Coding:
    return Coding(coding_id=coding_id, variable=variable, value=value, code=code)


def test_list_codings_builds_filter_and_calls_sdk():
    sdk = MagicMock()
    sdk.codings.list.return_value = []
    wf = CodingReviewWorkflow(sdk)

    with patch("imednet.workflows.coding_review.build_filter_string", return_value="foo") as bfs:
        result = wf.list_codings("ST", {"a": 1}, page_size=10)

    sdk.codings.list.assert_called_once_with("ST", filter="foo", page_size=10)
    bfs.assert_called_once_with({"a": 1})
    assert result == []


def test_get_uncoded_items_filters_empty_codes():
    sdk = MagicMock()
    codings = [
        _make_coding(1, "AE", "Headache", ""),
        _make_coding(2, "AE", "Headache", "A1"),
        _make_coding(3, "AE", "Nausea", ""),
    ]
    sdk.codings.list.return_value = codings
    wf = CodingReviewWorkflow(sdk)

    result = wf.get_uncoded_items("ST")

    assert result == [codings[0], codings[2]]


def test_get_inconsistent_codings_detects_multiple_codes():
    sdk = MagicMock()
    codings = [
        _make_coding(1, "AE", "Headache", "A1"),
        _make_coding(2, "AE", "Headache", "B2"),
        _make_coding(3, "AE", "Nausea", "A1"),
    ]
    sdk.codings.list.return_value = codings
    wf = CodingReviewWorkflow(sdk)

    result = wf.get_inconsistent_codings("ST")

    assert codings[0] in result and codings[1] in result
    assert codings[2] not in result
