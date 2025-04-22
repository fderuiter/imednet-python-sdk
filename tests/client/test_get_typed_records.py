"""Tests specifically for the get_typed_records method."""

from datetime import date, datetime
from unittest.mock import patch

import pytest
from pydantic import BaseModel

from imednet_sdk.api._base import ApiResponse, Metadata, PaginationInfo
from imednet_sdk.api.records import RecordModel
from imednet_sdk.api.variables import VariableModel
from imednet_sdk.exceptions import ApiError

# --- Mock Data for get_typed_records --- #
MOCK_STUDY_KEY_TYPED = "STUDY_XYZ"
MOCK_FORM_KEY_TYPED = "DEMO_FORM"

MOCK_VARIABLES_META_TYPED = [
    VariableModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        variableId=101,
        variableType="textField",
        variableName="patient_name",
        sequence=1,
        revision=1,
        disabled=False,
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        formId=201,
        variableOid="VAR_NAME",
        deleted=False,
        formKey=MOCK_FORM_KEY_TYPED,
        formName="Demo Form",
        label="Patient Name",
        blinded=False,
    ),
    VariableModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        variableId=102,
        variableType="integerField",
        variableName="patient_age",
        sequence=2,
        revision=1,
        disabled=False,
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        formId=201,
        variableOid="VAR_AGE",
        deleted=False,
        formKey=MOCK_FORM_KEY_TYPED,
        formName="Demo Form",
        label="Patient Age",
        blinded=False,
    ),
    VariableModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        variableId=103,
        variableType="dateField",
        variableName="visit_date",
        sequence=3,
        revision=1,
        disabled=False,
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        formId=201,
        variableOid="VAR_DATE",
        deleted=False,
        formKey=MOCK_FORM_KEY_TYPED,
        formName="Demo Form",
        label="Visit Date",
        blinded=False,
    ),
]

MOCK_VARIABLES_RESPONSE_TYPED: dict = {  # Added type hint
    "data": [
        {"variableName": "SUBJID", "dataType": "Text"},
        {"variableName": "VISITDT", "dataType": "Date"},
        {"variableName": "WEIGHT", "dataType": "Number", "numberDecimalPlaces": 1},
        {"variableName": "TEMP", "dataType": "Number", "numberDecimalPlaces": 1},
        {"variableName": "AE", "dataType": "Text"},
    ],
    "pagination": {"page": 0, "size": 5, "totalElements": 5, "totalPages": 1},
}

MOCK_RAW_RECORDS_TYPED = [
    RecordModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        intervalId=301,
        formId=201,
        formKey=MOCK_FORM_KEY_TYPED,
        siteId=401,
        recordId=501,
        recordOid="REC_001",
        recordType="CRF",
        recordStatus="Complete",
        subjectId=601,
        subjectOid="SUB_001",
        subjectKey="Subject 001",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        visitId=1,
        parentRecordId=None,  # Added missing required field
        deleted=False,  # Added missing required field
        recordData={
            "patient_name": "Alice",
            "patient_age": 42,
            "visit_date": "2023-05-20",
            "extra_field": "ignored",
        },
    ),
    RecordModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        intervalId=302,
        formId=201,
        formKey=MOCK_FORM_KEY_TYPED,
        siteId=401,
        recordId=502,
        recordOid="REC_002",
        recordType="CRF",
        recordStatus="Incomplete",
        subjectId=602,
        subjectOid="SUB_002",
        subjectKey="Subject 002",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        visitId=1,
        parentRecordId=None,  # Added missing required field
        deleted=False,  # Added missing required field
        recordData={
            "patient_name": "Bob",
            "patient_age": "thirty-five",  # Invalid age type
            "visit_date": "2023-05-21",
        },
    ),
    RecordModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        intervalId=303,
        formId=201,
        formKey=MOCK_FORM_KEY_TYPED,
        siteId=402,
        recordId=503,
        recordOid="REC_003",
        recordType="CRF",
        recordStatus="Complete",
        subjectId=603,
        subjectOid="SUB_003",
        subjectKey="Subject 003",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        visitId=1,
        parentRecordId=None,  # Added missing required field
        deleted=False,  # Added missing required field
        recordData={},
    ),
    RecordModel(
        studyKey=MOCK_STUDY_KEY_TYPED,
        intervalId=304,
        formId=201,
        formKey=MOCK_FORM_KEY_TYPED,
        siteId=402,
        recordId=504,
        recordOid="REC_004",
        recordType="CRF",
        recordStatus="Complete",
        subjectId=604,
        subjectOid="SUB_004",
        subjectKey="Subject 004",
        dateCreated=datetime.now(),
        dateModified=datetime.now(),
        visitId=1,
        parentRecordId=None,  # Added missing required field
        deleted=False,  # Added missing required field
        recordData={
            "patient_name": "Charlie",
            # Missing age and date
        },
    ),
]

MOCK_RECORDS_RESPONSE_TYPED: dict = {  # Added type hint
    "data": [
        {
            "recordId": 101,
            "formKey": "VITALS",
            "subjectKey": "SUBJ-001",
            "intervalName": "Screening",
            "dateCreated": "2023-01-15T10:00:00Z",
            "data": {
                "VISITDT": "2023-01-15",
                "WEIGHT": 70.5,
                "TEMP": 37.0,
            },
        },
        {
            "recordId": 102,
            "formKey": "AE",
            "subjectKey": "SUBJ-001",
            "intervalName": "Screening",
            "dateCreated": "2023-01-15T11:00:00Z",
            "data": {"AE": "Headache"},
        },
        {
            "recordId": 103,
            "formKey": "VITALS",
            "subjectKey": "SUBJ-001",
            "intervalName": "Week 4",
            "dateCreated": "2023-02-12T09:30:00Z",
            "data": {
                "VISITDT": "2023-02-12",
                "WEIGHT": 71.0,
                "TEMP": 36.8,
            },
        },
    ],
    "pagination": {"page": 0, "size": 3, "totalElements": 3, "totalPages": 1},
}

# --- Tests for get_typed_records --- #


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_success(mock_records_client, mock_variables_client, default_client):
    """Test successful fetching and parsing of typed records."""
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_records_client.list_records.return_value = MOCK_RECORDS_RESPONSE_TYPED

    typed_records = default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED)

    mock_variables_client.list_variables.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED, filter=f"formKey=={MOCK_FORM_KEY_TYPED}"
    )
    mock_records_client.list_records.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED, filter=f"formKey=={MOCK_FORM_KEY_TYPED}"
    )

    # Expecting 3 valid records (501, 503, 504), record 502 should fail validation
    assert len(typed_records) == 3

    # Check first valid record (Alice - 501)
    record1 = typed_records[0]
    assert isinstance(record1, BaseModel)
    assert hasattr(record1, "patient_name")
    assert hasattr(record1, "patient_age")
    assert hasattr(record1, "visit_date")
    assert record1.patient_name == "Alice"
    assert record1.patient_age == 42
    assert record1.visit_date == date(2023, 5, 20)
    assert not hasattr(record1, "extra_field")  # Check extra='ignore'

    # Check second valid record (Subject 003 - 503, empty data)
    record2 = typed_records[1]
    assert isinstance(record2, BaseModel)
    assert record2.patient_name is None  # Optional field with no data
    assert record2.patient_age is None  # Optional field with no data
    assert record2.visit_date is None  # Optional field with no data

    # Check third valid record (Charlie - 504, missing optional fields)
    record3 = typed_records[2]
    assert isinstance(record3, BaseModel)
    assert record3.patient_name == "Charlie"
    assert record3.patient_age is None
    assert record3.visit_date is None


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_no_variables(mock_records_client, mock_variables_client, default_client):
    """Test get_typed_records returns empty list when no variables are found."""
    empty_vars_response = ApiResponse(
        metadata=Metadata(
            status="OK", method="GET", path="/vars", timestamp=datetime.now(), error={}
        ),
        pagination=PaginationInfo(currentPage=0, size=0, totalPages=0, totalElements=0, sort=[]),
        data=[],
    )
    mock_variables_client.list_variables.return_value = empty_vars_response

    typed_records = default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, "NON_EXISTENT_FORM")

    mock_variables_client.list_variables.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED, filter="formKey==NON_EXISTENT_FORM"
    )
    mock_records_client.list_records.assert_not_called()  # Should not fetch records if no model
    assert typed_records == []


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_no_records(mock_records_client, mock_variables_client, default_client):
    """Test get_typed_records returns empty list when no records are found."""
    empty_records_response = ApiResponse(
        metadata=Metadata(
            status="OK", method="GET", path="/records", timestamp=datetime.now(), error={}
        ),
        pagination=PaginationInfo(currentPage=0, size=0, totalPages=0, totalElements=0, sort=[]),
        data=[],
    )
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_records_client.list_records.return_value = empty_records_response

    typed_records = default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED)

    mock_variables_client.list_variables.assert_called_once()
    mock_records_client.list_records.assert_called_once()
    assert typed_records == []


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_variable_fetch_error(
    mock_records_client, mock_variables_client, default_client
):
    """Test get_typed_records raises exception if variable fetching fails."""
    mock_variables_client.list_variables.side_effect = ApiError(
        "Failed to fetch vars", status_code=500
    )

    with pytest.raises(ApiError, match="Failed to fetch vars"):
        default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED)

    mock_variables_client.list_variables.assert_called_once()
    mock_records_client.list_records.assert_not_called()


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
@patch("imednet_sdk.utils.build_model_from_variables")  # Patch the function in utils
def test_get_typed_records_model_build_error(
    mock_build_model, mock_records_client, mock_variables_client, default_client
):
    """Test get_typed_records raises exception if model building fails."""
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_build_model.side_effect = ValueError("Invalid variable metadata")

    with pytest.raises(ValueError, match="Invalid variable metadata"):
        default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED)

    mock_variables_client.list_variables.assert_called_once()
    mock_build_model.assert_called_once()  # Check the patched function was called
    mock_records_client.list_records.assert_not_called()


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_record_fetch_error(
    mock_records_client, mock_variables_client, default_client
):
    """Test get_typed_records raises exception if record fetching fails."""
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_records_client.list_records.side_effect = ApiError(
        "Failed to fetch records", status_code=500
    )

    with pytest.raises(ApiError, match="Failed to fetch records"):
        default_client.get_typed_records(MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED)

    mock_variables_client.list_variables.assert_called_once()
    mock_records_client.list_records.assert_called_once()


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_with_kwargs(mock_records_client, mock_variables_client, default_client):
    """Test get_typed_records passes kwargs to list_records."""
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_records_client.list_records.return_value = MOCK_RECORDS_RESPONSE_TYPED

    default_client.get_typed_records(
        MOCK_STUDY_KEY_TYPED,
        MOCK_FORM_KEY_TYPED,
        size=10,
        sort="recordId,desc",
        record_data_filter="patient_age>30",
    )

    mock_variables_client.list_variables.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED, filter=f"formKey=={MOCK_FORM_KEY_TYPED}"
    )
    mock_records_client.list_records.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED,
        filter=f"formKey=={MOCK_FORM_KEY_TYPED}",
        size=10,
        sort="recordId,desc",
        record_data_filter="patient_age>30",
    )


@patch("imednet_sdk.client.ImednetClient.variables")
@patch("imednet_sdk.client.ImednetClient.records")
def test_get_typed_records_with_existing_filter_kwarg(
    mock_records_client, mock_variables_client, default_client
):
    """Test get_typed_records combines existing filter kwarg with formKey filter."""
    mock_variables_client.list_variables.return_value = MOCK_VARIABLES_RESPONSE_TYPED
    mock_records_client.list_records.return_value = MOCK_RECORDS_RESPONSE_TYPED

    existing_filter = "siteId==401"
    default_client.get_typed_records(
        MOCK_STUDY_KEY_TYPED, MOCK_FORM_KEY_TYPED, filter=existing_filter
    )

    mock_variables_client.list_variables.assert_called_once()
    expected_combined_filter = f"({existing_filter}) and formKey=={MOCK_FORM_KEY_TYPED}"
    mock_records_client.list_records.assert_called_once_with(
        MOCK_STUDY_KEY_TYPED, filter=expected_combined_filter
    )
