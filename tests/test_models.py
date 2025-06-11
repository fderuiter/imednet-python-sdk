from imednet_py.base import IMNModel
from imednet_py.models import Meta, Pagination, Envelope, Study, Meta, Sort
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


def test_envelope_model() -> None:
    meta = Meta(
        status="success",
        method="GET",
        path="/studies",
        timestamp="2025-06-11T00:00:00Z",
    )
    pagination = Pagination(
        current_page=0,
        page_size=1,
        total_pages=1,
        total_records=1,
    )
    env = Envelope[Study](
        metadata=meta,
        pagination=pagination,
        data=[Study(key="S1")],
    )

    dumped = env.model_dump()
    assert "currentPage" in dumped["pagination"]
    assert env.data[0].key == "S1"


def test_envelope_validation() -> None:
    payload = {
        "metadata": {
            "status": "success",
            "method": "GET",
            "path": "/studies",
            "timestamp": "2025-06-11T00:00:00Z",
        },
        "pagination": {
            "currentPage": 0,
            "pageSize": 1,
            "totalPages": 1,
            "totalRecords": 1,
        },
        "data": [{"key": "S1"}],
    }

    env = Envelope[Study].model_validate(payload)
    assert env.metadata.status == "success"
    assert len(env.data) == 1

def test_sort_round_trip() -> None:
    sort = Sort(property_="studyKey", direction="ASC")
    dumped = sort.model_dump(by_alias=True)
    assert dumped == {"property": "studyKey", "direction": "ASC"}
    reloaded = Sort.model_validate(dumped)
    assert reloaded.property_ == "studyKey"
    assert reloaded.direction == "ASC"
