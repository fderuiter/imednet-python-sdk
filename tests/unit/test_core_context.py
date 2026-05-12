import pytest

from imednet.core.context import get_current_study, reset_study_context, set_study_context
from imednet.errors.validation import ConfigurationError


def test_set_and_reset_study_context() -> None:
    token = set_study_context("S1")
    assert get_current_study() == "S1"
    reset_study_context(token)
    with pytest.raises(ConfigurationError):
        get_current_study()
