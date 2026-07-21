"""Unit tests for UATWorkflow orchestrator."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from imednet.spi.models import Form, Interval, Site, Variable
from imednet_workflows.uat.generator import GeneratedRecordSet
from imednet_workflows.uat.inspector import StudySnapshot
from imednet_workflows.uat.models import RecordTestType, UATSpecification
from imednet_workflows.uat.orchestrator import UATRunResult, UATSpecificationBuilder, UATWorkflow
from imednet_workflows.uat.submission import SubmissionResult


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    sdk.get_job.return_value = MagicMock(state="COMPLETED")
    return sdk


@pytest.fixture
def snapshot():
    return StudySnapshot(
        study_key="TEST_STUDY",
        forms=[
            Form(form_key="F1", form_name="Enrollment", form_type="Enrollment"),
            Form(form_key="F2", form_name="Scheduled", form_type="DataEntry"),
            Form(
                form_key="F3",
                form_name="Unscheduled",
                form_type="DataEntry",
                unscheduled_visit=True,
            ),
        ],
        variables=[
            Variable(form_key="F1", variable_name="V1", variable_key="VK1", variable_type="Text"),
            Variable(form_key="F2", variable_name="V2", variable_key="VK2", variable_type="Number"),
            Variable(form_key="F3", variable_name="V3", variable_key="VK3", variable_type="Date"),
        ],
        intervals=[
            Interval(
                interval_name="Int1",
                forms=[{"form_id": 1, "form_key": "F2", "form_name": "Scheduled"}],
            ),
        ],
        sites=[
            Site(site_name="Site1", site_enrollment_status="Active"),
        ],
    )


def test_builder_builds_spec(snapshot):
    builder = UATSpecificationBuilder()
    spec = builder.build(snapshot, subject_count=3)

    assert spec.study_key == "TEST_STUDY"
    assert len(spec.subject_specs) == 1
    assert spec.subject_specs[0].subject_count == 3
    assert len(spec.form_specs) == 3

    f1_spec = next(f for f in spec.form_specs if f.form_key == "F1")
    assert f1_spec.test_type == RecordTestType.REGISTER_SUBJECT

    f2_spec = next(f for f in spec.form_specs if f.form_key == "F2")
    assert f2_spec.test_type == RecordTestType.UPDATE_SCHEDULED_RECORD
    assert f2_spec.interval_name == "Int1"

    f3_spec = next(f for f in spec.form_specs if f.form_key == "F3")
    assert f3_spec.test_type == RecordTestType.CREATE_NEW_RECORD


def test_builder_builds_spec_with_no_active_sites(snapshot):
    snapshot.sites[0].site_enrollment_status = "Closed"
    builder = UATSpecificationBuilder()
    spec = builder.build(snapshot)
    assert spec.subject_specs[0].site_name == "Site1"

    snapshot.sites = []
    spec = builder.build(snapshot)
    assert spec.subject_specs[0].site_name == "Default Site"


def test_workflow_run_pipeline(mock_sdk, snapshot):
    workflow = UATWorkflow(mock_sdk)

    # Mock all internal methods
    workflow.inspect = MagicMock(return_value=snapshot)

    mock_spec = MagicMock(spec=UATSpecification)
    workflow.build_spec = MagicMock(return_value=mock_spec)

    mock_record_sets = [MagicMock(spec=GeneratedRecordSet)]
    workflow.generate = MagicMock(return_value=mock_record_sets)

    mock_submission = MagicMock(spec=SubmissionResult)
    mock_submission.total_records_submitted = 10
    mock_submission.all_batch_ids = ["B1"]
    workflow.submit = MagicMock(return_value=mock_submission)

    mock_poll_summary = MagicMock()
    mock_poll_summary.all_successful = True
    mock_poll_summary.results = {"B1": MagicMock()}
    mock_poll_summary.failures = {}
    workflow.monitor = MagicMock(return_value=mock_poll_summary)

    result = workflow.run("TEST_STUDY")

    assert isinstance(result, UATRunResult)
    assert result.study_key == "TEST_STUDY"
    assert result.overall_success is True
    assert result.record_sets == mock_record_sets
    assert "inspect" in result.phase_durations
    assert "monitor" in result.phase_durations

    summary = result.summary()
    assert "TEST_STUDY" in summary
    assert "PASS" in summary


def test_workflow_run_with_custom_spec(mock_sdk, snapshot):
    workflow = UATWorkflow(mock_sdk)
    workflow.inspect = MagicMock(return_value=snapshot)

    # Need a real UATSpecification or a better mock for the generator
    custom_spec = UATSpecification(
        study_key="TEST_STUDY",
        study_name="TEST_STUDY",
        subject_specs=[],
        form_specs=[],
    )

    with patch.object(workflow, "build_spec") as mock_build_spec:
        with patch.object(workflow, "generate", return_value=[]) as mock_generate:
            with patch.object(workflow, "submit", return_value=MagicMock(spec=SubmissionResult)):
                with patch.object(workflow, "monitor", return_value=MagicMock()):
                    workflow.run("TEST_STUDY", spec=custom_spec)
                    mock_build_spec.assert_not_called()
                    mock_generate.assert_called_once()


def test_workflow_run_result_overall_success():
    poll_summary = MagicMock()
    poll_summary.all_successful = True

    result = UATRunResult(
        study_key="S",
        started_at=datetime.now(timezone.utc),
        spec=MagicMock(spec=UATSpecification),
        record_sets=[],
        submission_result=MagicMock(spec=SubmissionResult),
        poll_summary=poll_summary,
    )
    assert result.overall_success is True

    poll_summary.all_successful = False
    assert result.overall_success is False


def test_workflow_individual_phases(mock_sdk, snapshot):
    workflow = UATWorkflow(mock_sdk)
    with patch.object(workflow, "_inspector") as mock_insp:
        mock_insp.inspect.return_value = snapshot
        assert workflow.inspect("S") == snapshot

    spec = MagicMock(spec=UATSpecification)
    with patch.object(workflow, "_generator") as mock_gen:
        mock_gen.generate.return_value = []
        assert workflow.generate(spec, snapshot) == []

    with patch.object(workflow, "_submitter") as mock_sub:
        mock_sub.submit.return_value = MagicMock()
        assert workflow.submit("S", []) is not None

    with patch.object(workflow, "_poller") as mock_poll:
        mock_poll.poll_many.return_value = MagicMock()
        assert workflow.monitor("S", MagicMock()) is not None
