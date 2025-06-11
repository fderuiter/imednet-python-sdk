from imednet_py.base import IMNModel
from imednet_py.models import Meta
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
