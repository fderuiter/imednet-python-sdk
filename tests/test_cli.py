import os
from unittest.mock import MagicMock, patch

import pytest
import typer
from imednet.cli import (
    extract_records,
    get_sdk,
    hello,
    list_sites,
    list_studies,
    list_subjects,
    list_users,
    parse_filter_args,
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


@patch("imednet.cli.print")
def test_hello(mock_print):
    hello("Tester")
    mock_print.assert_called_with("Hello Tester")

    hello()
    mock_print.assert_called_with("Hello World")
