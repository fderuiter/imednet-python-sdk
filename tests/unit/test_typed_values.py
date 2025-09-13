import pytest

from imednet.testing import typed_values


def test_value_for_each_type() -> None:
    assert typed_values.value_for("text") == "example"
    assert typed_values.value_for("date") == "2024-01-01"
    assert typed_values.value_for("integer") == 1
    assert typed_values.value_for("radio") == "1"
    assert typed_values.value_for("dropdown") == "1"
    assert typed_values.value_for("memo") == "example memo"
    assert typed_values.value_for("checkbox") is True


def test_canonical_type_synonyms() -> None:
    assert typed_values.canonical_type("Text") == "string"
    assert typed_values.canonical_type("int") == "number"


def test_typed_value_unsupported_type() -> None:
    from tests.live.conftest import _typed_value

    with pytest.raises(ValueError, match="No typed value for 'unsupported'"):
        _typed_value("unsupported")
