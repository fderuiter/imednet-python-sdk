import datetime
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Coding:
    study_key: str
    site_name: str
    site_id: int
    subject_id: int
    subject_key: str
    form_id: int
    form_name: str
    form_key: str
    revision: int
    record_id: int
    variable: str
    value: str
    coding_id: int
    code: str
    coded_by: str
    reason: str
    dictionary_name: str
    dictionary_version: str
    date_coded: datetime.datetime

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Coding":
        """
        Create a Coding instance from JSON data.

        Args:
            data: Dictionary containing coding data from the API

        Returns:
            Coding instance with the data
        """
        # Parse datetime string
        date_coded = (
            datetime.datetime.fromisoformat(data.get("dateCoded", "").replace(" ", "T"))
            if data.get("dateCoded")
            else datetime.datetime.now()
        )

        return cls(
            study_key=data.get("studyKey", ""),
            site_name=data.get("siteName", ""),
            site_id=data.get("siteId", 0),
            subject_id=data.get("subjectId", 0),
            subject_key=data.get("subjectKey", ""),
            form_id=data.get("formId", 0),
            form_name=data.get("formName", ""),
            form_key=data.get("formKey", ""),
            revision=data.get("revision", 0),
            record_id=data.get("recordId", 0),
            variable=data.get("variable", ""),
            value=data.get("value", ""),
            coding_id=data.get("codingId", 0),
            code=data.get("code", ""),
            coded_by=data.get("codedBy", ""),
            reason=data.get("reason", ""),
            dictionary_name=data.get("dictionaryName", ""),
            dictionary_version=data.get("dictionaryVersion", ""),
            date_coded=date_coded,
        )
