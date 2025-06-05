import os
from unittest.mock import MagicMock, patch

from imednet.webui import create_app


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "STUDY"))
@patch("imednet.webui.ImednetSDK")
def test_list_studies(mock_sdk, _mock_creds):
    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.studies.list.return_value = [MagicMock(study_key="S1", study_name="Study 1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies")
        assert resp.status_code == 200
        assert "Study 1" in resp.get_data(as_text=True)


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "STUDY"))
@patch("imednet.webui.ImednetSDK")
def test_list_subjects(mock_sdk, _mock_creds):
    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.subjects.list.return_value = [MagicMock(subject_key="SUBJ1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies/TEST/subjects")
        assert resp.status_code == 200
        assert "SUBJ1" in resp.get_data(as_text=True)


@patch.dict(os.environ, {}, clear=True)
@patch("imednet.webui.resolve_credentials")
@patch("imednet.webui.ImednetSDK")
def test_webui_uses_stored_credentials(mock_sdk, mock_resolve):
    mock_resolve.return_value = ("saved", "secret", "STUDY1")

    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.studies.list.return_value = []

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies")
        assert resp.status_code == 200
    mock_sdk.assert_called_once_with(
        api_key="saved",
        security_key="secret",
        base_url="https://edc.prod.imednetapi.com",
    )
