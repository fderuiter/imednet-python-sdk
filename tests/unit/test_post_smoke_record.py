"""Test Post Smoke Record module."""

import logging
from unittest.mock import Mock

import pytest
import scripts.post_smoke_record as smoke

from imednet.models.intervals import Interval
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.models.variables import Variable
from imednet.testing import typed_values


def test_submit_record_uses_configured_timeout() -> None:
    """Test the test submit record uses configured timeout functionality."""
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="COMPLETED", batch_id="B1")

    batch_id = smoke.submit_record(sdk, "ST", {"data": {}}, timeout=123)

    assert batch_id == "B1"
    sdk.poll_job.assert_called_once_with("ST", "B1", interval=1, timeout=123)


def test_submit_record_reports_failure_details() -> None:
    """Test the test submit record reports failure details functionality."""
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(
        state="FAILED",
        batch_id="B1",
        result_url="https://x",
        results="Form with formKey of SS not found.",
    )

    with pytest.raises(RuntimeError, match="FAILED: Form with formKey"):
        smoke.submit_record(sdk, "ST", {"data": {}}, timeout=1)


def _var(name: str, var_type: str) -> Variable:
    """Test the var functionality."""
    return Variable(variable_name=name, variable_type=var_type, form_id=1, form_key="F1")


def test_build_record_returns_typed_values() -> None:
    """Test the test build record returns typed values functionality."""
    sdk = Mock()
    sdk.variables.list.return_value = [
        _var("text", "text"),
        _var("date", "date"),
        _var("num", "integer"),
        _var("rad", "radio"),
        _var("drop", "dropdown"),
        _var("memo", "memo"),
        _var("check", "checkbox"),
        _var("extra", "text"),
    ]

    record = smoke.build_record(sdk, "ST", "F1")

    expected = {
        "text": typed_values.value_for("text"),
        "date": typed_values.value_for("date"),
        "num": typed_values.value_for("integer"),
        "rad": typed_values.value_for("radio"),
        "drop": typed_values.value_for("dropdown"),
        "memo": typed_values.value_for("memo"),
        "check": typed_values.value_for("checkbox"),
    }
    assert record == {
        "formKey": "F1",
        "data": expected,
    }
    sdk.variables.list.assert_called_once_with(study_key="ST", formKey="F1")


@pytest.mark.parametrize(
    "kwargs, extra",
    [
        ({"site_name": "S"}, {"siteName": "S"}),
        ({"subject_key": "SUB"}, {"subjectKey": "SUB"}),
        ({"interval_name": "INT"}, {"intervalName": "INT"}),
        (
            {
                "site_name": "S",
                "subject_key": "SUB",
                "interval_name": "INT",
            },
            {
                "siteName": "S",
                "subjectKey": "SUB",
                "intervalName": "INT",
            },
        ),
    ],
)
def test_build_record_optional_identifiers(kwargs: dict[str, str], extra: dict[str, str]) -> None:
    """Test the test build record optional identifiers functionality."""
    sdk = Mock()
    sdk.variables.list.return_value = []

    record = smoke.build_record(sdk, "ST", "F1", **kwargs)

    assert record == {"formKey": "F1", "data": {}} | extra
    sdk.variables.list.assert_called_once_with(study_key="ST", formKey="F1")


def test_discover_identifiers_returns_all() -> None:
    """Test the test discover identifiers returns all functionality."""
    sdk = Mock()
    sdk.sites.list.return_value = [
        Site(study_key="S", site_name="SITE", site_enrollment_status="Active")
    ]
    sdk.subjects.list.return_value = [
        Subject(study_key="S", subject_key="SUB", subject_status="Active")
    ]
    sdk.intervals.list.return_value = [Interval(study_key="S", interval_name="INT", disabled=False)]

    identifiers = smoke.discover_identifiers(sdk, "S")

    assert identifiers == ("SITE", "SUB", "INT")
    sdk.sites.list.assert_called_once_with(study_key="S")
    sdk.subjects.list.assert_called_once_with(study_key="S")
    sdk.intervals.list.assert_called_once_with(study_key="S")


def test_discover_identifiers_reports_missing(monkeypatch, capsys) -> None:
    """Test the test discover identifiers reports missing functionality."""
    monkeypatch.setattr(smoke, "discover_site_name", Mock(side_effect=Exception("no site")))
    monkeypatch.setattr(smoke, "discover_subject_key", Mock(side_effect=Exception("no subject")))
    monkeypatch.setattr(smoke, "discover_interval_name", Mock(side_effect=Exception("no int")))

    identifiers = smoke.discover_identifiers(Mock(), "S")

    assert identifiers == (None, None, None)
    out = capsys.readouterr().out
    assert "no site" in out
    assert "no subject" in out
    assert "no int" in out


def test_main_verbose_logs(monkeypatch, caplog) -> None:
    """Test the test main verbose logs functionality."""
    sdk = Mock()
    sdk.__enter__ = Mock(return_value=sdk)
    sdk.__exit__ = Mock(return_value=False)
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="COMPLETED", batch_id="B1")
    monkeypatch.setattr(smoke, "authenticate", Mock(return_value=sdk))
    monkeypatch.setattr(smoke, "discover_keys", Mock(return_value=("ST", "F1")))
    monkeypatch.setattr(smoke, "discover_identifiers", Mock(return_value=(None, "SUB", None)))
    monkeypatch.setattr(
        smoke,
        "build_record",
        Mock(return_value={"formKey": "F1", "data": {"x": 1}, "subjectKey": "SUB"}),
    )

    with caplog.at_level(logging.DEBUG):
        smoke.main(["-v"])

    logs = "\n".join(caplog.messages)
    assert "study_key=ST" in logs
    assert "Scenarios: [{'subject_key': 'SUB'}]" in logs
    assert "'data': '***'" in logs
    assert "Batch B1 COMPLETED" in logs


def test_main_returns_skip_when_identifiers_missing(monkeypatch, capsys) -> None:
    """Test the test main returns skip when identifiers missing functionality."""
    sdk = Mock()
    sdk.__enter__ = Mock(return_value=sdk)
    sdk.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(smoke, "authenticate", Mock(return_value=sdk))
    monkeypatch.setattr(smoke, "discover_keys", Mock(return_value=("ST", "F1")))
    monkeypatch.setattr(smoke, "discover_identifiers", Mock(return_value=(None, None, None)))

    exit_code = smoke.main([])

    assert exit_code == smoke.SKIP_EXIT_CODE
    out = capsys.readouterr().out
    assert "Smoke record skipped" in out


def test_main_returns_skip_on_discovery_failure(monkeypatch, capsys) -> None:
    """Test the test main returns skip on discovery failure functionality."""
    sdk = Mock()
    sdk.__enter__ = Mock(return_value=sdk)
    sdk.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(smoke, "authenticate", Mock(return_value=sdk))
    monkeypatch.setattr(smoke, "discover_keys", Mock(side_effect=Exception("no active studies")))

    exit_code = smoke.main([])

    assert exit_code == smoke.SKIP_EXIT_CODE
    err = capsys.readouterr().err
    assert "no active studies" in err
