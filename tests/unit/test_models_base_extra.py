import datetime

from imednet.models.base import ApiResponse, Error, Metadata, Pagination, SortField


def test_sort_field_defaults():
    model = SortField.model_validate({"property": None, "direction": None})
    assert model.property == ""
    assert model.direction == ""


def test_pagination_aliases_and_defaults():
    data = {
        "currentPage": "2",
        "size": "5",
        "totalPages": "3",
        "totalElements": "10",
        "sort": [{"property": "p", "direction": "ASC"}],
    }
    model = Pagination.model_validate(data)
    assert model.current_page == 2
    assert model.size == 5
    assert model.total_pages == 3
    assert model.total_elements == 10
    assert model.sort[0].property == "p"


def test_error_and_metadata_parsing():
    err = Error.model_validate({"details": {"foo": "bar"}})
    assert err.code == ""
    assert err.message == ""
    assert err.details == {"foo": "bar"}

    metadata = Metadata.model_validate(
        {
            "timestamp": "2023-01-01T00:00:00Z",
        }
    )
    assert metadata.status == ""
    assert metadata.method == ""
    assert metadata.path == ""
    assert isinstance(metadata.timestamp, datetime.datetime)


def test_api_response_generic():
    resp = ApiResponse[int].model_validate(
        {
            "metadata": {"timestamp": "2023-01-01T00:00:00Z"},
            "data": 5,
        }
    )
    assert resp.data == 5
