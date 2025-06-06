from unittest.mock import MagicMock

import pandas as pd
import pytest
from imednet.models.sites import Site
from imednet.models.subjects import Subject
from imednet.workflows.subject_enrollment_dashboard import SubjectEnrollmentDashboard


@pytest.fixture
def mock_sdk():
    return MagicMock()


def test_dashboard_build(mock_sdk):
    site1 = Site(study_key="S", site_id=1, site_name="Site 1", site_enrollment_status="ACTIVE")
    site2 = Site(study_key="S", site_id=2, site_name="Site 2", site_enrollment_status="ACTIVE")
    mock_sdk.sites.list.return_value = [site1, site2]

    subj1 = Subject(
        study_key="S",
        subject_id=1,
        subject_oid="O1",
        subject_key="SUBJ1",
        subject_status="ENROLLED",
        site_id=1,
        enrollment_start_date="2024-01-01T00:00:00",
    )
    subj2 = Subject(
        study_key="S",
        subject_id=2,
        subject_oid="O2",
        subject_key="SUBJ2",
        subject_status="WITHDRAWN",
        site_id=1,
        enrollment_start_date="2024-01-05T00:00:00",
    )
    subj3 = Subject(
        study_key="S",
        subject_id=3,
        subject_oid="O3",
        subject_key="SUBJ3",
        subject_status="ENROLLED",
        site_id=2,
        enrollment_start_date="2024-02-01T00:00:00",
    )
    mock_sdk.subjects.list.return_value = [subj1, subj2, subj3]

    dashboard = SubjectEnrollmentDashboard(mock_sdk)
    df = dashboard.build("S")
    assert isinstance(df, pd.DataFrame)
    row = df.set_index("site_id")
    assert row.loc[1, "subject_count"] == 2
    assert row.loc[1, "dropout_count"] == 1
    assert row.loc[1, "dropout_rate"] == 0.5
    assert row.loc[2, "subject_count"] == 1
    assert row.loc[2, "dropout_count"] == 0
    assert row.loc[2, "dropout_rate"] == 0
