from unittest.mock import MagicMock

import pytest
from imednet.models.studies import Study
from imednet.workflows.credential_validation import CredentialValidationWorkflow


def test_validate_environment_found(monkeypatch):
    sdk = MagicMock()
    sdk.studies.list.return_value = [
        Study.model_validate({"studyKey": "ABC"}),
        Study.model_validate({"studyKey": "XYZ"}),
    ]
    monkeypatch.setenv("IMEDNET_STUDY_KEY", "XYZ")
    workflow = CredentialValidationWorkflow(sdk)
    assert workflow.validate_environment() is True


def test_validate_environment_missing(monkeypatch):
    sdk = MagicMock()
    workflow = CredentialValidationWorkflow(sdk)
    monkeypatch.delenv("IMEDNET_STUDY_KEY", raising=False)
    with pytest.raises(ValueError):
        workflow.validate_environment()


def test_validate_false_when_not_found(monkeypatch):
    sdk = MagicMock()
    sdk.studies.list.return_value = [Study.model_validate({"studyKey": "ABC"})]
    workflow = CredentialValidationWorkflow(sdk)
    assert workflow.validate("XYZ") is False
