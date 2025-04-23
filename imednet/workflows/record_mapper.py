from typing import Any, Dict, List, Optional, Type

import pandas as pd
from pydantic import BaseModel, Field, create_model

from imednet.endpoints.records import Record as RecordModel
from imednet.endpoints.variables import Variable as VariableModel
from imednet.sdk import ImednetSDK


class RecordMapper:
    """
    Maps all EDC records for a study into a pandas DataFrame with human-readable
    column names by:
      1. Fetching all variable definitions for the study
      2. Dynamically creating a Pydantic model for recordData fields
      3. Fetching all records for the study (optionally filtered by visit)
      4. Merging metadata and recordData into a single DataFrame

    Example:
        sdk = ImednetSDK(api_key, security_key, base_url)
        mapper = RecordMapper(sdk)
        df = mapper.dataframe(study_key="MYSTUDY", visit_key=None)
    """

    def __init__(
        self,
        sdk: ImednetSDK,
        page_size: int = 500,
    ):
        """
        :param sdk: An initialized ImednetSDK instance (with API credentials)
        :param page_size: maximum items to fetch per request
        """
        self.sdk = sdk
        self.page_size = page_size

    def dataframe(self, study_key: str, visit_key: Optional[str] = None) -> pd.DataFrame:
        """
        Fetches all variables and records for a study (and optional visit) and returns a DataFrame.

        :param study_key: unique identifier for the study
        :param visit_key: optional visit key to filter records
        :return: pandas DataFrame with metadata columns + one column per variable
        """
        # 1. Fetch all variable metadata for the study
        vars_all: List[VariableModel] = self.sdk.variables.list(study_key=study_key)
        if not vars_all:
            raise ValueError(f"No variables found for study '{study_key}'")
        # Extract variable names and labels
        variable_keys = [v.variable_name for v in vars_all]
        label_map: Dict[str, str] = {v.variable_name: v.label for v in vars_all}

        # 2. Build dynamic Pydantic model for recordData
        fields: Dict[str, tuple] = {
            key: (Optional[Any], Field(None, alias=key, description=label_map[key]))
            for key in variable_keys
        }
        # Use keyword __base__ to satisfy Pydantic overload; ignore mypy for this call
        RecordDataModel: Type[BaseModel] = create_model(
            "RecordData",
            __base__=BaseModel,
            **fields,  # type: ignore
        )

        # 3. Fetch all records for the study
        recs_all: List[RecordModel] = self.sdk.records.list(study_key=study_key)
        # Optionally filter by visit
        if visit_key is not None:
            recs_all = [r for r in recs_all if str(r.visit_id) == str(visit_key)]

        # 4. Parse each record
        rows: List[Dict[str, Any]] = []
        for r in recs_all:
            # Metadata fields
            meta = {
                "recordId": r.record_id,
                "subjectKey": r.subject_key,
                "visitId": r.visit_id,
                "formId": r.form_id,
                "recordStatus": r.record_status,
                "dateCreated": r.date_created.isoformat(),
            }
            # Parse recordData through dynamic model
            parsed = RecordDataModel(**r.record_data).dict(by_alias=False)
            rows.append({**meta, **parsed})

        # 5. Build DataFrame
        df = pd.DataFrame(rows)
        if df.empty:
            return df  # no rows to reorder or rename
        # Reorder columns: metadata first, then variables
        meta_cols = ["recordId", "subjectKey", "visitId", "formId", "recordStatus", "dateCreated"]
        df = df[meta_cols + variable_keys]

        # 6. Rename variable columns to human-readable labels
        return df.rename(columns={key: label_map.get(key, key) for key in df.columns})
