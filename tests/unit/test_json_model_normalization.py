"""Unit tests for json model normalization."""

from datetime import datetime, timezone
from typing import Any

from imednet.models.base import ImednetBaseModel


class SampleModel(ImednetBaseModel):
    """Test suite for SampleModel."""

    flag: bool
    count: int
    timestamp: datetime
    names: list[str]
    mapping: dict[str, int]


def test_json_model_normalization() -> None:
    """Test that json model normalization."""
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


class SampleOptionalModel(ImednetBaseModel):
    """Test suite for SampleOptionalModel."""

    opt_str: str | None = None
    opt_int: int | None = None
    opt_bool: bool | None = None
    opt_datetime: datetime | None = None


def test_json_model_normalization_optional_fields() -> None:
    """Test that json model normalization optional fields."""
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
    """Test that json model normalization union field."""

    class SampleUnionModel(ImednetBaseModel):
        """Test suite for SampleUnionModel."""

        union_field: int | str

    model_int = SampleUnionModel(union_field="5")
    assert model_int.union_field == "5"  # No normalization for complex Union


def test_json_model_identity_normalizer() -> None:
    """Test that json model identity normalizer."""

    class SampleIdentityModel(ImednetBaseModel):
        """Test suite for SampleIdentityModel."""

        identity_field: Any

    model = SampleIdentityModel(identity_field=None)
    assert model.identity_field is None


def test_json_model_normalization_missing_field() -> None:
    """Test that json model normalization missing field."""

    class SampleModelMissing(ImednetBaseModel):
        """Test suite for SampleModelMissing."""

        opt_str: str | None = None

    model = SampleModelMissing.from_json({})
    assert model.opt_str is None


def test_json_model_from_json_method() -> None:
    """Test that json model from json method."""
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


def test_json_model_structural_shift(caplog):
    """Test that json model structural shift."""
    import logging

    class NestedModel(ImednetBaseModel):
        """Test suite for NestedModel."""

        id: int

    class TestModel(ImednetBaseModel):
        """Test suite for Model."""

        nested: NestedModel
        items: list[NestedModel]

    with caplog.at_level(logging.WARNING):
        # API returns list instead of object for `nested`
        # API returns object instead of list for `items`
        model = TestModel.from_json({"nested": [{"id": 1}], "items": {"id": 2}})
        assert model.nested.id == 1
        assert len(model.items) == 1
        assert model.items[0].id == 2
        assert "Structural shift detected" in caplog.text
