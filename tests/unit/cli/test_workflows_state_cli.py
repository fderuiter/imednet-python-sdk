"""Tests for the imednet_workflows state CLI subcommands."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from imednet_workflows.cli import state_app
from imednet_workflows.state_ledger import LedgerState, StreamState, StudyState


@pytest.fixture()
def runner() -> CliRunner:
    """TODO: Add docstring."""
    return CliRunner()


def _make_ledger_state(study_key: str, stream_name: str) -> LedgerState:
    """TODO: Add docstring."""
    ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
    return LedgerState(
        studies={
            study_key: StudyState(
                streams={
                    stream_name: StreamState(
                        last_timestamp=ts,
                        records_processed=42,
                        last_run_status="success",
                    )
                }
            )
        }
    )


class TestShowState:
    """TODO: Add docstring."""

    def test_show_all_entries(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        state = _make_ledger_state("STUDY-01", "records")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.read_state.return_value = state
            result = runner.invoke(state_app, ["show", "--ledger-path", ledger_path])

        assert result.exit_code == 0

    def test_show_filters_by_study_key(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        state = _make_ledger_state("STUDY-01", "records")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.read_state.return_value = state
            result = runner.invoke(
                state_app,
                ["show", "--ledger-path", ledger_path, "--study-key", "STUDY-01"],
            )

        assert result.exit_code == 0

    def test_show_no_matching_entries_prints_warning(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.read_state.return_value = LedgerState()
            result = runner.invoke(state_app, ["show", "--ledger-path", ledger_path])

        assert result.exit_code == 0
        assert "No ledger entries" in result.output

    def test_show_error_on_read_failure(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.read_state.side_effect = OSError("cannot read")
            result = runner.invoke(state_app, ["show", "--ledger-path", ledger_path])

        assert result.exit_code == 1


class TestSetState:
    """TODO: Add docstring."""

    def test_set_valid_utc_timestamp(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            result = runner.invoke(
                state_app,
                [
                    "set",
                    "--study-key",
                    "STUDY-01",
                    "--stream",
                    "records",
                    "--timestamp",
                    "2026-05-22T12:00:00Z",
                    "--ledger-path",
                    ledger_path,
                ],
            )
            mock_ledger.return_value.set_last_timestamp.assert_called_once()

        assert result.exit_code == 0
        assert "Successfully set" in result.output

    def test_set_with_records_processed(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            result = runner.invoke(
                state_app,
                [
                    "set",
                    "--study-key",
                    "STUDY-01",
                    "--stream",
                    "records",
                    "--timestamp",
                    "2026-05-22T12:00:00+00:00",
                    "--records-processed",
                    "100",
                    "--ledger-path",
                    ledger_path,
                ],
            )
            call_kwargs = mock_ledger.return_value.set_last_timestamp.call_args.kwargs
            assert call_kwargs["records_processed"] == 100
            expected_ts = datetime(2026, 5, 22, 12, 0, 0, tzinfo=timezone.utc)
            assert call_kwargs["timestamp"] == expected_ts

        assert result.exit_code == 0

    def test_set_invalid_timestamp_exits_with_error(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        result = runner.invoke(
            state_app,
            [
                "set",
                "--study-key",
                "STUDY-01",
                "--stream",
                "records",
                "--timestamp",
                "not-a-timestamp",
                "--ledger-path",
                ledger_path,
            ],
        )
        assert result.exit_code == 1
        assert "Invalid ISO timestamp" in result.output

    def test_set_write_failure_exits_with_error(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.set_last_timestamp.side_effect = OSError(
                "disk full"
            )
            result = runner.invoke(
                state_app,
                [
                    "set",
                    "--study-key",
                    "STUDY-01",
                    "--stream",
                    "records",
                    "--timestamp",
                    "2026-05-22T12:00:00Z",
                    "--ledger-path",
                    ledger_path,
                ],
            )

        assert result.exit_code == 1
        assert "Failed to write ledger" in result.output


class TestResetState:
    """TODO: Add docstring."""

    def test_reset_whole_study_when_found(self, runner: CliRunner, tmp_path) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.delete_entry.return_value = True
            result = runner.invoke(
                state_app,
                ["reset", "--study-key", "STUDY-01", "--ledger-path", ledger_path],
            )
            mock_ledger.return_value.delete_entry.assert_called_once_with("STUDY-01")

        assert result.exit_code == 0
        assert "Successfully reset all streams" in result.output

    def test_reset_specific_stream_when_found(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.delete_entry.return_value = True
            result = runner.invoke(
                state_app,
                [
                    "reset",
                    "--study-key",
                    "STUDY-01",
                    "--stream",
                    "records",
                    "--ledger-path",
                    ledger_path,
                ],
            )
            mock_ledger.return_value.delete_entry.assert_called_once_with(
                "STUDY-01", "records"
            )

        assert result.exit_code == 0
        assert "Successfully reset stream" in result.output

    def test_reset_study_not_found_prints_warning(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.delete_entry.return_value = False
            result = runner.invoke(
                state_app,
                ["reset", "--study-key", "NONEXISTENT", "--ledger-path", ledger_path],
            )

        assert result.exit_code == 0
        assert "No state found" in result.output

    def test_reset_stream_not_found_prints_warning(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.delete_entry.return_value = False
            result = runner.invoke(
                state_app,
                [
                    "reset",
                    "--study-key",
                    "STUDY-01",
                    "--stream",
                    "nonexistent",
                    "--ledger-path",
                    ledger_path,
                ],
            )

        assert result.exit_code == 0
        assert "No stream" in result.output

    def test_reset_exception_exits_with_error(
        self, runner: CliRunner, tmp_path
    ) -> None:
        """TODO: Add docstring."""
        ledger_path = str(tmp_path / "ledger.json")
        with patch("imednet_workflows.cli.ExtractionStateLedger") as mock_ledger:
            mock_ledger.return_value.delete_entry.side_effect = OSError("locked")
            result = runner.invoke(
                state_app,
                ["reset", "--study-key", "STUDY-01", "--ledger-path", ledger_path],
            )

        assert result.exit_code == 1
        assert "Failed to reset ledger state" in result.output
