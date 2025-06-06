from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from imednet.models.queries import Query
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.workflows.site_performance import SitePerformanceWorkflow


@pytest.fixture
def mock_sdk():
    sdk = MagicMock()
    sdk.sites.list = MagicMock()
    sdk.subjects.list = MagicMock()
    return sdk


def make_site(site_id: int, status: str = "Active") -> Site:
    return Site(
        study_key="ST",
        site_id=site_id,
        site_name=f"Site {site_id}",
        site_enrollment_status=status,
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
    )


def make_subject(subject_id: int, site_id: int) -> Subject:
    return Subject(
        study_key="ST",
        subject_id=subject_id,
        subject_oid=f"S{subject_id}",
        subject_key=f"SUBJ{subject_id}",
        subject_status="Enrolled",
        site_id=site_id,
        site_name=f"Site {site_id}",
        deleted=False,
        enrollment_start_date="2024-01-01T00:00:00",
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
        keywords=[],
    )


def make_query(subject_id: int) -> Query:
    return Query(
        study_key="ST",
        subject_id=subject_id,
        subject_oid=f"S{subject_id}",
        annotation_type="",
        annotation_id=1,
        description="",
        record_id=1,
        variable="",
        subject_key=f"SUBJ{subject_id}",
        date_created="2024-01-01T00:00:00",
        date_modified="2024-01-01T00:00:00",
        query_comments=[],
    )


@patch("imednet.workflows.site_performance.QueryManagementWorkflow")
def test_get_site_metrics(mock_qm_class, mock_sdk):
    mock_sdk.sites.list.return_value = [make_site(1), make_site(2)]
    mock_sdk.subjects.list.return_value = [
        make_subject(1, 1),
        make_subject(2, 1),
        make_subject(3, 2),
    ]

    mock_qm = mock_qm_class.return_value
    mock_qm.get_open_queries.return_value = [make_query(1), make_query(3)]

    wf = SitePerformanceWorkflow(mock_sdk)
    df = wf.get_site_metrics("ST")

    assert isinstance(df, pd.DataFrame)
    row1 = df[df["site_id"] == 1].iloc[0]
    row2 = df[df["site_id"] == 2].iloc[0]

    assert row1["subject_count"] == 2
    assert row1["open_query_count"] == 1
    assert row2["subject_count"] == 1
    assert row2["open_query_count"] == 1
    mock_qm.get_open_queries.assert_called_once_with("ST")


@patch("imednet.workflows.site_performance.QueryManagementWorkflow")
def test_get_site_metrics_unknown_subject(mock_qm_class, mock_sdk):
    mock_sdk.sites.list.return_value = [make_site(1)]
    mock_sdk.subjects.list.return_value = [make_subject(1, 1)]

    mock_qm = mock_qm_class.return_value
    # Query for subject not in the list should be ignored
    mock_qm.get_open_queries.return_value = [make_query(999)]

    wf = SitePerformanceWorkflow(mock_sdk)
    df = wf.get_site_metrics("ST")

    assert df.loc[0, "open_query_count"] == 0
