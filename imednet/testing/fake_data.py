"""Utility functions for generating fake API payloads."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from faker import Faker

from imednet.models.forms import Form
from imednet.models.variables import Variable
from imednet.validation.cache import SchemaCache

faker = Faker()


def _timestamp() -> str:
    """Generate a fake timestamp string in the format 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        A formatted datetime string.
    """
    return faker.date_time().strftime("%Y-%m-%d %H:%M:%S")


def fake_subject() -> Dict[str, Any]:
    """Generate a dictionary representing a fake subject API payload.

    Returns:
        A dictionary with fake subject data.
    """
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
    """Generate a dictionary representing a fake site API payload.

    Returns:
        A dictionary with fake site data.
    """
    return {
        "studyKey": faker.bothify(text="??????"),
        "siteId": faker.random_int(min=1, max=10000),
        "siteName": faker.company(),
        "siteEnrollmentStatus": faker.random_element(["Enrollment Open", "Enrollment Closed"]),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
    }


def fake_interval() -> Dict[str, Any]:
    """Generate a dictionary representing a fake interval API payload.

    Returns:
        A dictionary with fake interval data.
    """
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
    """Generate a dictionary representing a fake query API payload.

    Returns:
        A dictionary with fake query data.
    """
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


def _fake_value(var_type: str) -> Any:
    """Generate a fake value for a given variable type.

    Args:
        var_type: The type of the variable (e.g., "int", "float", "bool").

    Returns:
        A fake value of the specified type.
    """
    var_type = var_type.lower()
    if var_type in {"int", "integer", "number"}:
        return faker.random_int(min=0, max=100)
    if var_type in {"float", "decimal"}:
        return faker.pyfloat(left_digits=2, right_digits=2, positive=True)
    if var_type in {"bool", "boolean"}:
        return faker.boolean()
    return faker.word()


def fake_record(schema: Optional[SchemaCache] = None) -> Dict[str, Any]:
    """Generate a dictionary representing a fake record API payload.

    If a schema is provided, the `recordData` will be generated with values
    that match the variable types in the schema.

    Args:
        schema: An optional schema cache to use for generating typed data.

    Returns:
        A dictionary with fake record data.
    """
    if schema and schema._form_variables:
        form_key = faker.random_element(list(schema._form_variables))
        variables = schema.variables_for_form(form_key)
        first_var = next(iter(variables.values()))
        form_id = first_var.form_id
        record_data = {name: _fake_value(var.variable_type) for name, var in variables.items()}
        return {
            "studyKey": faker.bothify(text="??????"),
            "intervalId": faker.random_int(min=1, max=10000),
            "formId": form_id,
            "formKey": form_key,
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
            "recordData": record_data,
        }

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


def fake_form() -> Dict[str, Any]:
    """Generate a dictionary representing a fake form API payload.

    Returns:
        A dictionary with fake form data.
    """
    return {
        "studyKey": faker.bothify(text="??????"),
        "formId": faker.random_int(min=1, max=10000),
        "formKey": faker.lexify(text="????"),
        "formName": faker.word().title(),
        "formType": faker.random_element(["CRF", "Diary"]),
        "revision": faker.random_int(min=1, max=10),
        "embeddedLog": faker.boolean(),
        "enforceOwnership": faker.boolean(),
        "userAgreement": faker.boolean(),
        "subjectRecordReport": faker.boolean(),
        "unscheduledVisit": faker.boolean(),
        "otherForms": faker.boolean(),
        "eproForm": faker.boolean(),
        "allowCopy": faker.boolean(),
        "disabled": faker.boolean(),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
    }


def fake_variable() -> Dict[str, Any]:
    """Generate a dictionary representing a fake variable API payload.

    Returns:
        A dictionary with fake variable data.
    """
    return {
        "studyKey": faker.bothify(text="??????"),
        "variableId": faker.random_int(min=1, max=10000),
        "variableType": faker.random_element(["text", "integer", "date"]),
        "variableName": faker.lexify(text="????"),
        "sequence": faker.random_int(min=1, max=100),
        "revision": faker.random_int(min=1, max=10),
        "disabled": faker.boolean(),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
        "formId": faker.random_int(min=1, max=10000),
        "variableOid": faker.uuid4(),
        "deleted": faker.boolean(),
        "formKey": faker.lexify(text="????"),
        "formName": faker.word().title(),
        "label": faker.word().title(),
        "blinded": faker.boolean(),
    }


def fake_forms_for_cache(num_forms: int = 1, study_key: Optional[str] = None) -> List[Form]:
    """Generate a list of `Form` model objects for use in tests.

    Args:
        num_forms: The number of forms to generate.
        study_key: An optional study key to assign to the forms.

    Returns:
        A list of `Form` model objects.
    """
    forms: List[Form] = []
    for _ in range(num_forms):
        data = fake_form()
        if study_key is not None:
            data["studyKey"] = study_key
        forms.append(Form.from_json(data))
    return forms


def fake_variables_for_cache(
    forms: List[Form],
    vars_per_form: int = 1,
    study_key: Optional[str] = None,
) -> List[Variable]:
    """Generate a list of `Variable` model objects for a given list of forms.

    Args:
        forms: The list of forms to generate variables for.
        vars_per_form: The number of variables to generate for each form.
        study_key: An optional study key to assign to the variables.

    Returns:
        A list of `Variable` model objects.
    """
    variables: List[Variable] = []
    for form in forms:
        for _ in range(vars_per_form):
            data = fake_variable()
            data["formId"] = form.form_id
            data["formKey"] = form.form_key
            data["formName"] = form.form_name
            if study_key is not None:
                data["studyKey"] = study_key
            variables.append(Variable.from_json(data))
    return variables


def fake_visit() -> Dict[str, Any]:
    """Generate a dictionary representing a fake visit API payload.

    Returns:
        A dictionary with fake visit data.
    """
    return {
        "visitId": faker.random_int(min=1, max=10000),
        "studyKey": faker.bothify(text="??????"),
        "intervalId": faker.random_int(min=1, max=10000),
        "intervalName": faker.word().title(),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectKey": f"{faker.random_int(100, 999)}-{faker.random_int(100, 999)}",
        "startDate": _timestamp(),
        "endDate": _timestamp(),
        "dueDate": _timestamp(),
        "visitDate": _timestamp(),
        "visitDateForm": faker.word().title(),
        "visitDateQuestion": faker.word(),
        "deleted": False,
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
    }


def fake_coding() -> Dict[str, Any]:
    """Generate a dictionary representing a fake coding API payload.

    Returns:
        A dictionary with fake coding data.
    """
    return {
        "studyKey": faker.bothify(text="??????"),
        "siteName": faker.company(),
        "siteId": faker.random_int(min=1, max=10000),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectKey": f"{faker.random_int(100, 999)}-{faker.random_int(100, 999)}",
        "formId": faker.random_int(min=1, max=10000),
        "formName": faker.word().title(),
        "formKey": faker.lexify(text="????"),
        "revision": faker.random_int(min=1, max=5),
        "recordId": faker.random_int(min=1, max=10000),
        "variable": faker.lexify(text="????"),
        "value": faker.word(),
        "codingId": faker.random_int(min=1, max=10000),
        "code": faker.lexify(text="???"),
        "codedBy": faker.user_name(),
        "reason": faker.sentence(nb_words=3),
        "dictionaryName": faker.word().title(),
        "dictionaryVersion": str(faker.random_int(min=1, max=5)),
        "dateCoded": _timestamp(),
    }


def fake_record_revision() -> Dict[str, Any]:
    """Generate a dictionary representing a fake record revision API payload.

    Returns:
        A dictionary with fake record revision data.
    """
    return {
        "studyKey": faker.bothify(text="??????"),
        "recordRevisionId": faker.random_int(min=1, max=10000),
        "recordId": faker.random_int(min=1, max=10000),
        "recordOid": faker.uuid4(),
        "recordRevision": faker.random_int(min=1, max=10),
        "dataRevision": faker.random_int(min=1, max=10),
        "recordStatus": faker.random_element(["Record Incomplete", "Record Complete"]),
        "subjectId": faker.random_int(min=1, max=10000),
        "subjectOid": faker.uuid4(),
        "subjectKey": f"{faker.random_int(100, 999)}-{faker.random_int(100, 999)}",
        "siteId": faker.random_int(min=1, max=10000),
        "formKey": faker.lexify(text="????"),
        "intervalId": faker.random_int(min=1, max=10000),
        "role": faker.word(),
        "user": faker.user_name(),
        "reasonForChange": faker.sentence(nb_words=3),
        "deleted": False,
        "dateCreated": _timestamp(),
    }


def fake_study() -> Dict[str, Any]:
    """Generate a dictionary representing a fake study API payload.

    Returns:
        A dictionary with fake study data.
    """
    return {
        "sponsorKey": faker.lexify(text="????????"),
        "studyKey": faker.bothify(text="??????"),
        "studyId": faker.random_int(min=1, max=10000),
        "studyName": faker.word().title(),
        "studyDescription": faker.sentence(nb_words=3),
        "studyType": faker.random_element(["Clinical", "Observational", "Registry"]),
        "dateCreated": _timestamp(),
        "dateModified": _timestamp(),
    }


def fake_job() -> Dict[str, Any]:
    """Generate a dictionary representing a fake job API payload.

    Returns:
        A dictionary with fake job data.
    """
    return {
        "jobId": faker.uuid4(),
        "batchId": faker.lexify(text="????????"),
        "state": faker.random_element(["OPEN", "RUNNING", "COMPLETE"]),
        "dateCreated": _timestamp(),
        "dateStarted": _timestamp(),
        "dateFinished": _timestamp(),
    }


def fake_user() -> Dict[str, Any]:
    """Generate a dictionary representing a fake user API payload.

    Returns:
        A dictionary with fake user data.
    """
    return {
        "userId": faker.uuid4(),
        "login": faker.user_name(),
        "firstName": faker.first_name(),
        "lastName": faker.last_name(),
        "email": faker.email(),
        "userActiveInStudy": faker.boolean(),
        "roles": [
            {
                "dateCreated": _timestamp(),
                "dateModified": _timestamp(),
                "roleId": faker.lexify(text="????"),
                "communityId": faker.random_int(min=1, max=10000),
                "name": faker.word().title(),
                "description": faker.sentence(nb_words=3),
                "level": faker.random_int(min=1, max=5),
                "type": faker.word(),
                "inactive": faker.boolean(),
            }
        ],
    }


__all__ = [
    "fake_subject",
    "fake_site",
    "fake_interval",
    "fake_query",
    "fake_record",
    "fake_form",
    "fake_variable",
    "fake_forms_for_cache",
    "fake_variables_for_cache",
    "fake_visit",
    "fake_coding",
    "fake_record_revision",
    "fake_study",
    "fake_job",
    "fake_user",
]
