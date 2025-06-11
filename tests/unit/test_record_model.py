from imednet.models.base import Envelope
from imednet.models.records import Record


def test_record_envelope_roundtrip() -> None:
    record_payload = {
        "studyKey": "STU",
        "intervalId": 1,
        "formId": 2,
        "formKey": "DEMO",
        "siteId": 10,
        "recordId": 100,
        "recordOid": "OID123",
        "recordType": "scheduled",
        "recordStatus": "completed",
        "deleted": False,
        "dateCreated": "2025-06-01T10:00:00Z",
        "dateModified": "2025-06-01T12:00:00Z",
        "subjectId": 200,
        "subjectOid": "SUBJ123",
        "subjectKey": "SUBJKEY",
        "visitId": 1,
        "parentRecordId": 0,
        "keywords": [
            {
                "keywordName": "Test",
                "keywordKey": "TEST",
                "keywordId": 1,
                "dateAdded": "2025-06-01T09:00:00Z",
            }
        ],
        "recordData": {"AGE": 25, "SEX": "M"},
    }

    payload = {
        "metadata": {
            "status": "ok",
            "method": "GET",
            "path": "/records",
            "timestamp": "2025-06-01T12:00:00Z",
            "error": {"code": "", "message": "", "details": {}},
        },
        "pagination": {
            "currentPage": 0,
            "size": 1,
            "totalPages": 1,
            "totalElements": 1,
            "sort": [],
        },
        "data": [record_payload],
    }

    env = Envelope[list[Record]].model_validate(payload)
    rec = env.data[0]
    assert rec.model_dump(by_alias=True, exclude_none=True, mode="json") == record_payload
