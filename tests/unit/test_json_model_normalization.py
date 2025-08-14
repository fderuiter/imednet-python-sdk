from datetime import datetime, timezone

from imednet.models.json_base import JsonModel


class SampleModel(JsonModel):
    flag: bool
    count: int
    timestamp: datetime
    names: list[str]
    mapping: dict[str, int]


def test_json_model_normalization() -> None:
    model = SampleModel(
        flag="true",
        count="5",
        timestamp="2024-01-02T03:04:05Z",
        names="alice",
        mapping={"one": "1"},
    )

    assert model.flag is True
    assert model.count == 5
    assert model.timestamp == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert model.names == ["alice"]
    assert model.mapping == {"one": 1}
