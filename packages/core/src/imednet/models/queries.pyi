"""Query and annotation models for iMedNet."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from imednet.models.engine import ModelEngine
from imednet.models.json_base import JsonModel



class QueryComment(JsonModel):
    pass


class Query(JsonModel):
    study_key: Optional[str]
    subject_id: Optional[int]
    annotation_id: Optional[int]
    description: Optional[str]
    record_id: Optional[int]
    variable: Optional[str]
    subject_key: Optional[str]
    date_created: Optional[str]
    date_modified: Optional[str]
    annotation_type: Any
    subject_oid: Any
    type: Any

