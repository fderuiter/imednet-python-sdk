import os
from unittest.mock import MagicMock, patch

import pytest
import typer
from imednet.cli import (
    extract_records,
    get_sdk,
    hello,
    list_open_queries_cmd,
    list_sites,
    list_studies,
    list_subjects,
    list_users,
    parse_filter_args,
    query_state_counts_cmd,
    register_subjects_cmd,
    save_credentials_cmd,
)
from imednet.core.exceptions import ApiError


# Test SDK initialization
@patch.dict(
    os.environ, {"IMEDNET_API_KEY": "test_api_key", "IMEDNET_SECURITY_KEY": "test_security_key"}
)
@patch("imednet.cli.ImednetSDK")
def test_get_sdk_success(mock_sdk):
    mock_instance = MagicMock()
    mock_sdk.return_value = mock_instance

    ctx = MagicMock()
    ctx.obj = {}
    sdk = get_sdk(ctx)

    mock_sdk.assert_called_once_with(
        api_key="test_api_key",
        security_key="test_security_key",
        base_url="https://edc.prod.imednetapi.com",
    )
    assert sdk == mock_instance


@patch.dict(os.environ, {}, clear=True)
def test_get_sdk_missing_credentials():
    ctx = MagicMock()
    ctx.obj = {}
    with pytest.raises(typer.Exit) as excinfo:
        get_sdk(ctx)
    assert excinfo.value.exit_code == 1


@patch.dict(os.environ, {}, clear=True)
@patch("imednet.cli.resolve_credentials")
@patch("imednet.cli.ImednetSDK")
def test_get_sdk_from_saved(mock_sdk, mock_resolve):
    mock_resolve.return_value = ("saved", "secret", "STUDY1")
    mock_instance = MagicMock()
    mock_sdk.return_value = mock_instance

    ctx = MagicMock()
    ctx.obj = {}
    sdk = get_sdk(ctx)

    mock_sdk.assert_called_once_with(
        api_key="saved",
        security_key="secret",
        base_url="https://edc.prod.imednetapi.com",
    )
    assert os.environ["IMEDNET_STUDY_KEY"] == "STUDY1"
    assert sdk == mock_instance


@patch.dict(
    os.environ, {"IMEDNET_API_KEY": "test_api_key", "IMEDNET_SECURITY_KEY": "test_security_key"}
)
@patch("imednet.cli.ImednetSDK")
def test_get_sdk_exception(mock_sdk):
    mock_sdk.side_effect = Exception("SDK initialization error")
    ctx = MagicMock()
    ctx.obj = {}
    with pytest.raises(typer.Exit) as excinfo:
        get_sdk(ctx)
    assert excinfo.value.exit_code == 1


# Test parse_filter_args function
def test_parse_filter_args_none():
    result = parse_filter_args(None)
    assert result is None


def test_parse_filter_args_empty():
    result = parse_filter_args([])
    assert result is None


def test_parse_filter_args_valid():
    filters = ["key1=value1", "key2=true", "key3=false", "key4=123"]
    result = parse_filter_args(filters)
    expected = {"key1": "value1", "key2": True, "key3": False, "key4": 123}
    assert result == expected


def test_parse_filter_args_invalid_format():
    with pytest.raises(typer.Exit) as excinfo:
        parse_filter_args(["invalid_filter"])
    assert excinfo.value.exit_code == 1


# Test command functions
@patch("imednet.cli.get_sdk")
def test_list_studies_success(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.studies.list.return_value = ["Study1", "Study2"]

    ctx = MagicMock()
    ctx.obj = {}
    list_studies(ctx)

    mock_sdk.studies.list.assert_called_once()


@patch("imednet.cli.get_sdk")
def test_list_studies_empty(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.studies.list.return_value = []

    ctx = MagicMock()
    ctx.obj = {}
    list_studies(ctx)

    mock_sdk.studies.list.assert_called_once()


@patch("imednet.cli.get_sdk")
def test_list_studies_api_error(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.studies.list.side_effect = ApiError("API Error")
    ctx = MagicMock()
    ctx.obj = {}
    with pytest.raises(typer.Exit) as excinfo:
        list_studies(ctx)
    assert excinfo.value.exit_code == 1


@patch("imednet.cli.get_sdk")
def test_list_sites_success(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.sites.list.return_value = ["Site1", "Site2"]

    ctx = MagicMock()
    ctx.obj = {}
    list_sites(ctx, "STUDY1")

    mock_sdk.sites.list.assert_called_once_with("STUDY1")


@patch("imednet.cli.get_sdk")
def test_list_users_success(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.users.list.return_value = ["User1"]

    ctx = MagicMock()
    ctx.obj = {}
    list_users(ctx, "STUDY1", False)

    mock_sdk.users.list.assert_called_once_with("STUDY1", include_inactive=False)


@patch("imednet.cli.get_sdk")
def test_list_subjects_with_filter(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_sdk.subjects.list.return_value = ["Subject1", "Subject2"]

    with patch("imednet.cli.build_filter_string") as mock_build_filter:
        mock_build_filter.return_value = "status=active"
        ctx = MagicMock()
        ctx.obj = {}
        list_subjects(ctx, "STUDY1", ["status=active"])

        mock_build_filter.assert_called_once()
        mock_sdk.subjects.list.assert_called_once_with("STUDY1", filter="status=active")


@patch("imednet.cli.get_sdk")
def test_extract_records_success(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    mock_workflow = MagicMock()

    with patch("imednet.cli.DataExtractionWorkflow") as mock_workflow_class:
        mock_workflow_class.return_value = mock_workflow
        mock_workflow.extract_records_by_criteria.return_value = ["Record1", "Record2"]

        ctx = MagicMock()
        ctx.obj = {}
        extract_records(
            ctx,
            "STUDY1",
            record_filter=["form_key=DEMOG"],
            subject_filter=["status=active"],
            visit_filter=["visit_key=SCREENING"],
        )

        mock_workflow.extract_records_by_criteria.assert_called_once()


@patch("imednet.cli.get_sdk")
def test_list_open_queries(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    workflow_instance = MagicMock()
    with patch("imednet.cli.QueryManagementWorkflow") as mock_wf_cls:
        mock_wf_cls.return_value = workflow_instance
        workflow_instance.get_open_queries.return_value = ["Q1"]

        ctx = MagicMock()
        ctx.obj = {}
        list_open_queries_cmd(ctx, "STUDY1")

        workflow_instance.get_open_queries.assert_called_once_with("STUDY1")


@patch("imednet.cli.get_sdk")
def test_query_state_counts(mock_get_sdk):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    workflow_instance = MagicMock()
    with patch("imednet.cli.QueryManagementWorkflow") as mock_wf_cls:
        mock_wf_cls.return_value = workflow_instance
        workflow_instance.get_query_state_counts.return_value = {"open": 1}

        ctx = MagicMock()
        ctx.obj = {}
        query_state_counts_cmd(ctx, "STUDY1")

        workflow_instance.get_query_state_counts.assert_called_once_with("STUDY1")


@patch("imednet.cli.get_sdk")
def test_register_subjects_cmd(mock_get_sdk, tmp_path):
    mock_sdk = MagicMock()
    mock_get_sdk.return_value = mock_sdk
    workflow_instance = MagicMock()
    with patch("imednet.cli.RegisterSubjectsWorkflow") as mock_wf_cls:
        mock_wf_cls.return_value = workflow_instance

        data_file = tmp_path / "subs.json"
        data_file.write_text("[{}]")

        ctx = MagicMock()
        ctx.obj = {}
        register_subjects_cmd(ctx, "STUDY1", data_file, None)

        workflow_instance.register_subjects.assert_called_once()


@patch("imednet.cli.store_creds")
@patch("imednet.cli.typer.prompt")
def test_save_credentials_cmd(mock_prompt, mock_store):
    mock_prompt.side_effect = ["key", "sec", "STUDY", "pass", "pass"]
    save_credentials_cmd()
    mock_store.assert_called_once_with("key", "sec", "STUDY", "pass")


@patch("imednet.cli.print")
def test_hello(mock_print):
    hello("Tester")
    mock_print.assert_called_with("Hello Tester")

    hello()
    mock_print.assert_called_with("Hello World")
