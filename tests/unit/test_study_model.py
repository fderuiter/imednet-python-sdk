from __future__ import annotations

from imednet.models.studies import Study


def test_study_model_roundtrip() -> None:
    raw = {
        "sponsorKey": "SP1",
        "studyKey": "ST1",
        "studyId": 123,
        "studyName": "Study",
        "studyDescription": "Desc",
        "studyType": "EDC",
        "dateCreated": "2024-01-01T00:00:00Z",
        "dateModified": "2024-01-02T00:00:00Z",
    }
    study = Study.model_validate(raw)
    assert study.study_key == "ST1"
    assert study.sponsor_key == "SP1"
    dumped = study.model_dump(by_alias=True)
    assert dumped == raw
