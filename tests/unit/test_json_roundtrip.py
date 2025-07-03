import pytest
from imednet.models import Form, Job, Subject
from imednet.testing import fake_data


@pytest.mark.parametrize(
    "cls,payload_func",
    [
        (Subject, fake_data.fake_subject),
        (Form, fake_data.fake_form),
        (Job, fake_data.fake_job),
    ],
)
def test_json_roundtrip(cls, payload_func):
    payload = payload_func()
    model = cls.from_json(payload)
    dumped = model.model_dump(by_alias=True)
    assert cls.from_json(dumped) == model
