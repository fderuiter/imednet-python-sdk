from unittest.mock import patch


@patch("streamlit.title")
def test_component_gallery_renders(mock_title):
    import imednet_streamlit.pages.component_gallery  # noqa: F401

    mock_title.assert_called_once_with("Component Gallery")
