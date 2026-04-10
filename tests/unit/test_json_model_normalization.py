from datetime import datetime, timezone
from typing import Any, Optional, Union

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


class SampleOptionalModel(JsonModel):
    opt_str: Optional[str] = None
    opt_int: Optional[int] = None
    opt_bool: Optional[bool] = None
    opt_datetime: Optional[datetime] = None


def test_json_model_normalization_optional_fields() -> None:
    # Test with None values
    model_none = SampleOptionalModel(opt_str=None, opt_int=None, opt_bool=None, opt_datetime=None)
    assert model_none.opt_str is None
    assert model_none.opt_int is None
    assert model_none.opt_bool is None
    assert model_none.opt_datetime is None

    # Test with string values
    model_str = SampleOptionalModel(
        opt_str="hello", opt_int="5", opt_bool="true", opt_datetime="2024-01-02T03:04:05Z"
    )
    assert model_str.opt_str == "hello"
    assert model_str.opt_int == 5
    assert model_str.opt_bool is True
    assert model_str.opt_datetime == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


def test_json_model_normalization_union_field() -> None:
    class SampleUnionModel(JsonModel):
        union_field: Union[int, str]

    model_int = SampleUnionModel(union_field="5")
    assert model_int.union_field == "5"  # No normalization for complex Union


def test_json_model_identity_normalizer() -> None:
    class SampleIdentityModel(JsonModel):
        identity_field: Any

    model = SampleIdentityModel(identity_field=None)
    assert model.identity_field is None


def test_json_model_normalization_missing_field() -> None:
    class SampleModelMissing(JsonModel):
        opt_str: Optional[str] = None

    model = SampleModelMissing.from_json({})
    assert model.opt_str is None


def test_json_model_from_json_method() -> None:
    data = {
        "flag": "true",
        "count": "5",
        "timestamp": "2024-01-02T03:04:05Z",
        "names": "alice",
        "mapping": {"one": "1"},
    }
    model = SampleModel.from_json(data)
    assert model.flag is True
    assert model.count == 5
