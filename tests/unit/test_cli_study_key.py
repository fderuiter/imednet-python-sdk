import pytest
import typer
from imednet.cli import require_study_key


def test_require_study_key_returns_value() -> None:
    assert require_study_key("ABC") == "ABC"


def test_require_study_key_missing_exits() -> None:
    with pytest.raises(typer.Exit):
        require_study_key(None)
