import pytest

from imednet.core.context import (
    get_current_study,
    get_study_context,
    reset_study_context,
    set_study_context,
    study_context,
)
from imednet.errors.validation import ConfigurationError


def test_set_and_reset_study_context() -> None:
    token = set_study_context("S1")
    assert get_current_study() == "S1"
    reset_study_context(token)
    with pytest.raises(ConfigurationError):
        get_current_study()


def test_study_context_manager_resets_value() -> None:
    with study_context("S1"):
        assert get_current_study() == "S1"
        assert get_study_context() == "S1"

    assert get_study_context() is None
