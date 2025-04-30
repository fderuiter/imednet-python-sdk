from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from imednet.endpoints.codings import CodingsEndpoint
from imednet.models.codings import Coding

SAMPLE_CODING_DATA = {
    "studyKey": "STUDY1",
    "siteName": "Main Site",
    "siteId": 101,
    "subjectId": 202,
    "subjectKey": "SUBJ1",
    "formId": 303,
    "formName": "Form A",
    "formKey": "FORM_A",
    "revision": 1,
    "recordId": 404,
    "variable": "VAR1",
    "value": "Positive",
    "codingId": 505,
    "code": "A123",
    "codedBy": "coder1",
    "reason": "Initial coding",
    "dictionaryName": "MedDRA",
    "dictionaryVersion": "24.0",
    "dateCoded": "2023-10-27T10:00:00Z",
}


def test_coding_creation():
    coding = Coding.model_validate(SAMPLE_CODING_DATA)
    assert coding.study_key == "STUDY1"
    assert coding.site_name == "Main Site"
    assert coding.site_id == 101
    assert coding.subject_id == 202
    assert coding.subject_key == "SUBJ1"
    assert coding.form_id == 303
    assert coding.form_name == "Form A"
    assert coding.form_key == "FORM_A"
    assert coding.revision == 1
    assert coding.record_id == 404
    assert coding.variable == "VAR1"
    assert coding.value == "Positive"
    assert coding.coding_id == 505
    assert coding.code == "A123"
    assert coding.coded_by == "coder1"
    assert coding.reason == "Initial coding"
    assert coding.dictionary_name == "MedDRA"
    assert coding.dictionary_version == "24.0"
    assert coding.date_coded == datetime(2023, 10, 27, 10, 0, 0, tzinfo=timezone.utc)


def test_coding_defaults():
    coding = Coding.model_validate({})
    assert coding.study_key == ""
    assert coding.site_name == ""
    assert coding.site_id == 0
    assert coding.subject_id == 0
    assert coding.subject_key == ""
    assert coding.form_id == 0
    assert coding.form_name == ""
    assert coding.form_key == ""
    assert coding.revision == 0
    assert coding.record_id == 0
    assert coding.variable == ""
    assert coding.value == ""
    assert coding.coding_id == 0
    assert coding.code == ""
    assert coding.coded_by == ""
    assert coding.reason == ""
    assert coding.dictionary_name == ""
    assert coding.dictionary_version == ""
    assert isinstance(coding.date_coded, datetime)


def test_coding_str_and_int_parsing():
    data = {
        "studyKey": None,
        "siteName": None,
        "siteId": "123",
        "subjectId": "456",
        "formId": "789",
        "revision": "2",
        "recordId": "321",
        "codingId": "654",
        "variable": None,
        "value": None,
        "code": None,
        "codedBy": None,
        "reason": None,
        "dictionaryName": None,
        "dictionaryVersion": None,
        "dateCoded": "2024-01-01T12:00:00Z",
    }
    coding = Coding.model_validate(data)
    assert coding.site_id == 123
    assert coding.subject_id == 456
    assert coding.form_id == 789
    assert coding.revision == 2
    assert coding.record_id == 321
    assert coding.coding_id == 654
    assert coding.study_key == ""
    assert coding.variable == ""
    assert coding.value == ""
    assert coding.code == ""
    assert coding.coded_by == ""
    assert coding.reason == ""
    assert coding.dictionary_name == ""
    assert coding.dictionary_version == ""
    assert coding.date_coded == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    class DummyClient:
        pass

    @pytest.fixture
    def endpoint():
        ep = CodingsEndpoint(client=MagicMock())
        ep._auto_filter = MagicMock(side_effect=lambda x: x)
        ep._build_path = MagicMock(side_effect=lambda *args: "/mocked/path/" + "/".join(args))
        return ep

    def test_list_with_study_key_and_filters(endpoint):
        paginator_mock = MagicMock()
        paginator_mock.__iter__.return_value = [{"foo": "bar"}, {"baz": "qux"}]
        with (
            patch(
                "imednet.endpoints.codings.Paginator", return_value=paginator_mock
            ) as paginator_cls,
            patch(
                "imednet.endpoints.codings.Coding.from_json", side_effect=lambda x: x
            ) as from_json,
            patch(
                "imednet.endpoints.codings.build_filter_string", return_value="mocked_filter"
            ) as filter_str,
        ):
            result = endpoint.list(study_key="STUDY1", foo="bar", test=123)
            assert result == [{"foo": "bar"}, {"baz": "qux"}]
            endpoint._build_path.assert_called_once_with("STUDY1", "codings")
            paginator_cls.assert_called_once()
            assert from_json.call_count == 2
            assert filter_str.called

    def test_list_with_study_key_no_filters(endpoint):
        paginator_mock = MagicMock()
        paginator_mock.__iter__.return_value = [{"a": 1}]
        with (
            patch("imednet.endpoints.codings.Paginator", return_value=paginator_mock),
            patch("imednet.endpoints.codings.Coding.from_json", side_effect=lambda x: x),
        ):
            result = endpoint.list(study_key="STUDY2")
            assert result == [{"a": 1}]
            endpoint._build_path.assert_called_with("STUDY2", "codings")

    def test_list_with_study_key_in_filters(endpoint):
        paginator_mock = MagicMock()
        paginator_mock.__iter__.return_value = [{"foo": "bar"}]
        with (
            patch("imednet.endpoints.codings.Paginator", return_value=paginator_mock),
            patch("imednet.endpoints.codings.Coding.from_json", side_effect=lambda x: x),
        ):
            result = endpoint.list(studyKey="STUDY3")
            assert result == [{"foo": "bar"}]
            endpoint._build_path.assert_called_with("STUDY3", "codings")

    def test_list_raises_value_error_if_no_study_key(endpoint):
        with pytest.raises(ValueError, match="Study key must be provided"):
            endpoint.list()

    def test_get_success(endpoint):
        mock_json = {"data": [{"foo": "bar"}]}
        endpoint._client.get.return_value.json.return_value = mock_json
        with patch(
            "imednet.endpoints.codings.Coding.from_json", return_value="CODING_OBJ"
        ) as from_json:
            result = endpoint.get("STUDY4", "CODE123")
            endpoint._build_path.assert_called_with("STUDY4", "codings", "CODE123")
            endpoint._client.get.assert_called_once()
            assert result == "CODING_OBJ"
            from_json.assert_called_once_with({"foo": "bar"})

    def test_get_raises_value_error_if_not_found(endpoint):
        endpoint._client.get.return_value.json.return_value = {"data": []}
        with pytest.raises(ValueError, match="Coding CODE404 not found in study STUDY5"):
            endpoint.get("STUDY5", "CODE404")
