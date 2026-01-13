import pytest
from textual.app import App
from unittest.mock import MagicMock
from imednet.tui.form_builder import FormBuilderPane

@pytest.fixture
def mock_sdk():
    from imednet.sdk import ImednetSDK
    return MagicMock(spec=ImednetSDK)

def test_form_builder_pane_instantiation(mock_sdk):
    """Test that the FormBuilderPane can be instantiated."""
    pane = FormBuilderPane(sdk=mock_sdk)
    assert pane.sdk == mock_sdk
    # We can check if compose returns a generator/list but usually it's called by the App
    # Just verifying instantiation checks imports and __init__
