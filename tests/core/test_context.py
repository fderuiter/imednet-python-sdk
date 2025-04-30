from imednet.core.context import Context

"""
Tests for the Context class in the imednet.core.context module.
"""


def test_context_initialization():
    """Test that Context initializes with default_study_key as None."""
    context = Context()
    assert context.default_study_key is None


def test_set_default_study_key():
    """Test setting a default study key."""
    context = Context()
    study_key = "test-study-123"
    context.set_default_study_key(study_key)
    assert context.default_study_key == study_key


def test_clear_default_study_key():
    """Test clearing the default study key."""
    context = Context()
    study_key = "test-study-123"
    context.set_default_study_key(study_key)
    assert context.default_study_key == study_key

    context.clear_default_study_key()
    assert context.default_study_key is None


def test_default_study_key_dataclass_initialization():
    """Test initializing Context with a specific default_study_key."""
    study_key = "test-study-456"
    context = Context(default_study_key=study_key)
    assert context.default_study_key == study_key
