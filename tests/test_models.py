from imednet_py.base import IMNModel
from imednet_py.models import Meta, Pagination
from pydantic import Field


class Example(IMNModel):
    study_key: str = Field(..., alias="studyKey")


def test_alias_population() -> None:
    by_snake = Example(study_key="S1")
    assert by_snake.study_key == "S1"

    by_camel = Example(studyKey="S2")
    assert by_camel.study_key == "S2"


def test_meta_model() -> None:
    payload = {
        "status": "success",
        "method": "GET",
        "path": "/studies",
        "timestamp": "2025-06-11T00:00:00Z",
    }
    meta = Meta.model_validate(payload)

    assert meta.status == "success"
    assert meta.method == "GET"
    assert meta.path == "/studies"
    assert meta.timestamp == "2025-06-11T00:00:00Z"
    assert meta.error is None


def test_pagination_model() -> None:
    sample = {
        "pagination": {
            "currentPage": 1,
            "size": 10,
            "totalPages": 3,
            "totalElements": 25,
            "sort": [
                {"property": "updatedAt", "direction": "DESC"}
            ],
        }
    }

    pagination = Pagination.model_validate(sample["pagination"])

    assert pagination.current_page == 1
    assert pagination.size == 10
    assert pagination.total_pages == 3
    assert pagination.total_elements == 25
    assert isinstance(pagination.sort, list)
    assert pagination.sort[0].property == "updatedAt"
    assert pagination.sort[0].direction == "DESC"
