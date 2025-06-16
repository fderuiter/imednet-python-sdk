"""Utility functions for generating fake API payloads."""

from __future__ import annotations

from typing import Any, Dict

from faker import Faker

faker = Faker()


def _timestamp() -> str:
    """Return a formatted datetime string."""

    return faker.date_time().strftime("%Y-%m-%d %H:%M:%S")


def fake_subject() -> Dict[str, Any]:
    """Return a fake subject payload."""

    return {
        "studyKey": faker.bothify(text="??????"),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectOid": faker.uuid4(),
        "subjectKey": f"{faker.random_int(10, 99)}-{faker.random_int(100, 999)}",
        "subjectStatus": faker.random_element(["Enrolled", "Screened", "Completed"]),
        "siteId": faker.random_int(min=1, max=9999),
        "siteName": faker.company(),
        "deleted": False,
        "enrollmentStartDate": _timestamp(),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
        "keywords": [
            {
                "keywordName": faker.word().title(),
                "keywordKey": faker.lexify(text="???").upper(),
                "keywordId": faker.random_int(),
                "dateAdded": _timestamp(),
            }
        ],
    }


def fake_site() -> Dict[str, Any]:
    """Return a fake site payload."""

    return {
        "studyKey": faker.bothify(text="??????"),
        "siteId": faker.random_int(min=1, max=10000),
        "siteName": faker.company(),
        "siteEnrollmentStatus": faker.random_element(["Enrollment Open", "Enrollment Closed"]),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
    }


def fake_interval() -> Dict[str, Any]:
    """Return a fake interval payload."""

    return {
        "studyKey": faker.bothify(text="??????"),
        "intervalId": faker.random_int(min=1, max=10000),
        "intervalName": faker.word().title(),
        "intervalDescription": faker.sentence(nb_words=3),
        "intervalSequence": faker.random_int(min=1, max=500),
        "intervalGroupId": faker.random_int(min=1, max=100),
        "intervalGroupName": faker.word().title(),
        "disabled": faker.boolean(),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
        "timeline": "Start Date End Date",
        "definedUsingInterval": faker.word().title(),
        "windowCalculationForm": faker.word().title(),
        "windowCalculationDate": faker.lexify(text="????"),
        "actualDateForm": faker.word().title(),
        "actualDate": faker.lexify(text="????"),
        "dueDateWillBeIn": faker.random_int(min=1, max=60),
        "negativeSlack": faker.random_int(min=1, max=14),
        "positiveSlack": faker.random_int(min=1, max=14),
        "eproGracePeriod": faker.random_int(min=1, max=7),
        "forms": [
            {
                "formId": faker.random_int(min=1, max=10000),
                "formKey": faker.lexify(text="????"),
                "formName": faker.word().title(),
            }
        ],
    }


def fake_query() -> Dict[str, Any]:
    """Return a fake query payload."""

    return {
        "studyKey": faker.bothify(text="??????"),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectOid": faker.uuid4(),
        "annotationType": faker.random_element(["subject", "record", "question"]),
        "annotationId": faker.random_int(min=1, max=10000),
        "type": faker.random_element(["subject", "record", "question"]),
        "description": faker.sentence(nb_words=3),
        "recordId": faker.random_int(min=1, max=10000),
        "variable": faker.lexify(text="????"),
        "subjectKey": f"{faker.random_int(100, 999)}-{faker.random_int(100, 999)}",
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
        "queryComments": [
            {
                "sequence": 1,
                "annotationStatus": "Monitor Query Open",
                "user": faker.user_name(),
                "comment": faker.sentence(),
                "closed": False,
                "date": _timestamp(),
            }
        ],
    }


def fake_record() -> Dict[str, Any]:
    """Return a fake record payload."""

    return {
        "studyKey": faker.bothify(text="??????"),
        "intervalId": faker.random_int(min=1, max=10000),
        "formId": faker.random_int(min=1, max=10000),
        "formKey": faker.lexify(text="????"),
        "siteId": faker.random_int(min=1, max=10000),
        "recordId": faker.random_int(min=1, max=10000),
        "recordOid": faker.uuid4(),
        "recordType": "SUBJECT",
        "recordStatus": faker.random_element(["Record Incomplete", "Record Complete"]),
        "deleted": False,
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectOid": faker.uuid4(),
        "subjectKey": f"{faker.random_int(100, 999)}-{faker.random_int(100, 999)}",
        "visitId": faker.random_int(min=1, max=10000),
        "parentRecordId": faker.random_int(min=1, max=10000),
        "keywords": [
            {
                "keywordName": faker.word().title(),
                "keywordKey": faker.lexify(text="???").upper(),
                "keywordId": faker.random_int(),
                "dateAdded": _timestamp(),
            }
        ],
        "recordData": {
            "dateCreated": _timestamp(),
            "unvnum": str(faker.random_int(min=1, max=5)),
            "dateModified": _timestamp(),
            "aeser": "",
            "aeterm": faker.word().title(),
        },
    }


__all__ = [
    "fake_subject",
    "fake_site",
    "fake_interval",
    "fake_query",
    "fake_record",
]
