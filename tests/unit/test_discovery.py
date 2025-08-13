from unittest.mock import Mock

import pytest

from imednet.discovery import NoLiveDataError, discover_form_key
from imednet.models.forms import Form


def test_discover_form_key_chooses_subject_form() -> None:
    sdk = Mock()
    sdk.forms.list.return_value = [
        Form(study_key="S", form_key="SS", subject_record_report=False),
        Form(study_key="S", form_key="F1", subject_record_report=True, disabled=True),
        Form(study_key="S", form_key="F2", subject_record_report=True, disabled=False),
    ]

    assert discover_form_key(sdk, "S") == "F2"


def test_discover_form_key_raises_when_no_valid_forms() -> None:
    sdk = Mock()
    sdk.forms.list.return_value = [Form(study_key="S", form_key="SS", subject_record_report=False)]

    with pytest.raises(NoLiveDataError):
        discover_form_key(sdk, "S")
