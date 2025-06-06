import os
from unittest.mock import MagicMock, patch

from imednet.webui import create_app


@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "S1", "study_name": "Study 1"}],
)
def test_list_studies(_mock_list):
    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies")
        assert resp.status_code == 200
        assert "Study 1" in resp.get_data(as_text=True)


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "TEST", "study_name": "Study"}],
)
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "TEST"))
@patch("imednet.webui.ImednetSDK")
def test_list_subjects(mock_sdk, _mock_creds, _mock_list):
    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.subjects.list.return_value = [MagicMock(subject_key="SUBJ1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies/TEST/subjects")
        assert resp.status_code == 200
        assert "SUBJ1" in resp.get_data(as_text=True)


@patch("imednet.webui.list_credentials", return_value=[])
def test_webui_redirects_when_no_credentials(_mock_list):
    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies")
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/credentials/new")


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch("imednet.webui.save_credentials")
@patch("imednet.webui.ImednetSDK")
def test_credentials_form_saves(mock_sdk, mock_save):
    mock_sdk.return_value = MagicMock()

    app = create_app()
    with app.test_client() as client:
        resp = client.post(
            "/credentials/new",
            data={
                "api_key": "a",
                "security_key": "b",
                "study_key": "s",
                "study_name": "Study",
                "password": "pwd",
            },
        )
        assert resp.status_code == 302
    mock_save.assert_called_once_with("a", "b", "s", "Study", "pwd")


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "TEST", "study_name": "Study"}],
)
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "TEST"))
@patch("imednet.webui.ImednetSDK")
def test_list_sites(mock_sdk, _mock_creds, _mock_list):
    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.sites.list.return_value = [MagicMock(site_name="Site 1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies/TEST/sites")
        assert resp.status_code == 200
        assert "Site 1" in resp.get_data(as_text=True)


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "TEST", "study_name": "Study"}],
)
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "TEST"))
@patch("imednet.webui.ImednetSDK")
def test_list_users(mock_sdk, _mock_creds, _mock_list):
    instance = MagicMock()
    mock_sdk.return_value = instance
    instance.users.list.return_value = [MagicMock(user_name="User1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/users")
        assert resp.status_code == 200
        assert "User1" in resp.get_data(as_text=True)


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "TEST", "study_name": "Study"}],
)
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "TEST"))
@patch("imednet.webui.QueryManagementWorkflow")
@patch("imednet.webui.ImednetSDK")
def test_list_open_queries(mock_sdk, mock_qm_cls, _mock_creds, _mock_list):
    instance = MagicMock()
    mock_sdk.return_value = instance
    qm_instance = MagicMock()
    mock_qm_cls.return_value = qm_instance
    qm_instance.get_open_queries.return_value = [MagicMock(description="Q1")]

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/studies/TEST/queries/open")
        assert resp.status_code == 200
        assert "Q1" in resp.get_data(as_text=True)
    qm_instance.get_open_queries.assert_called_once_with("TEST")


@patch.dict(os.environ, {"IMEDNET_API_KEY": "key", "IMEDNET_SECURITY_KEY": "sec"})
@patch(
    "imednet.webui.list_credentials",
    return_value=[{"study_key": "TEST", "study_name": "Study"}],
)
@patch("imednet.webui.resolve_credentials", return_value=("key", "sec", "TEST"))
@patch("imednet.webui.RegisterSubjectsWorkflow")
@patch("imednet.webui.ImednetSDK")
def test_register_subjects(mock_sdk, mock_wf_cls, _mock_creds, _mock_list):
    instance = MagicMock()
    mock_sdk.return_value = instance
    wf_instance = MagicMock()
    mock_wf_cls.return_value = wf_instance

    app = create_app()
    with app.test_client() as client:
        resp = client.post(
            "/studies/TEST/register-subjects",
            data={"data": "[]"},
        )
        assert resp.status_code == 302
    wf_instance.register_subjects.assert_called_once()
