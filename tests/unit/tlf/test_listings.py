import pandas as pd
from unittest.mock import MagicMock

import pytest

from imednet.models import Subject
from imednet.sdk import ImednetSDK
from imednet.endpoints import SubjectsEndpoint
from imednet.tlf.listings import SubjectListing


@pytest.fixture
def mock_sdk():
    sdk = MagicMock(spec=ImednetSDK)
    sdk.subjects = MagicMock(spec=SubjectsEndpoint)
    return sdk


def test_subject_listing_generate(mock_sdk):
    # Arrange
    subjects_data = [
        Subject(
            subject_key="001",
            subject_status="Enrolled",
            site_name="Site A",
            enrollment_start_date="2023-01-01",
        ),
        Subject(
            subject_key="002",
            subject_status="Screened",
            site_name="Site B",
            enrollment_start_date="2023-01-02",
        ),
    ]
    mock_sdk.subjects.list.return_value = subjects_data
    report = SubjectListing(sdk=mock_sdk, study_key="test_study")

    # Act
    df = report.generate()

    # Assert
    mock_sdk.subjects.list.assert_called_once_with(study_key="test_study")
    assert not df.empty
    assert list(df.columns) == ["Subject ID", "Status", "Site", "Enrollment Date"]
    assert len(df) == 2
    assert df.iloc[0]["Subject ID"] == "001"
    assert df.iloc[1]["Site"] == "Site B"


def test_subject_listing_generate_no_subjects(mock_sdk):
    # Arrange
    mock_sdk.subjects.list.return_value = []
    report = SubjectListing(sdk=mock_sdk, study_key="test_study")

    # Act
    df = report.generate()

    # Assert
    assert df.empty
    assert list(df.columns) == ["Subject ID", "Status", "Site", "Enrollment Date"]
