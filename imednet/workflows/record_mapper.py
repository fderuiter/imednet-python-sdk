import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, create_model

from imednet.models.records import Record as RecordModel
from imednet.models.variables import Variable as VariableModel
from imednet.utils.filters import build_filter_string

if TYPE_CHECKING:
    from ..sdk import ImednetSDK

# Setup basic logging
logger = logging.getLogger(__name__)


class RecordMapper:
    """
    Maps EDC records for a study into a pandas DataFrame.

    Features:
      - Fetches variable definitions for column mapping.
      - Dynamically creates a Pydantic model for type validation of record data.
      - Fetches records, applying server-side filtering where possible.
      - Merges metadata and record data.
      - Offers choice between variable names or labels for column headers.
      - Handles parsing errors gracefully for individual records.

    Example:
        sdk = ImednetSDK(api_key, security_key, base_url)
        mapper = RecordMapper(sdk)
        # Get DataFrame with labels as columns, filtered by visit
        df_labels = mapper.dataframe(study_key="MYSTUDY", visit_key="VISIT1")
        # Get DataFrame with variable names as columns
        df_names = mapper.dataframe(study_key="MYSTUDY", use_labels_as_columns=False)
    """

    def __init__(
        self,
        sdk: "ImednetSDK",
    ):
        """
        :param sdk: An initialized ImednetSDK instance (with API credentials)
        """
        self.sdk = sdk

    def dataframe(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        use_labels_as_columns: bool = True,
    ) -> pd.DataFrame:
        """Return a DataFrame of records for ``study_key``."""
        variable_keys, label_map = self._fetch_variable_metadata(study_key)
        if not variable_keys:
            return pd.DataFrame()
        record_model = self._build_record_model(variable_keys, label_map)
        records = self._fetch_records(study_key, visit_key)
        rows, errors = self._parse_records(records, record_model)
        if errors:
            logger.warning("Encountered %s errors while parsing record data.", errors)
        dataframe = self._build_dataframe(rows, variable_keys, label_map, use_labels_as_columns)
        if dataframe.empty:
            logger.info(
                "No records processed successfully for study '%s' with the given filters.",
                study_key,
            )
        return dataframe

    def _fetch_variable_metadata(self, study_key: str) -> Tuple[List[str], Dict[str, str]]:
        """Return variable keys and a label map for ``study_key``."""
        variables: List[VariableModel] = self.sdk.variables.list(study_key=study_key)
        if not variables:
            logger.warning(
                "No variables found for study '%s'. Returning empty DataFrame.",
                study_key,
            )
            return [], {}

        keys = [v.variable_name for v in variables]
        labels = {v.variable_name: v.label for v in variables}
        return keys, labels

    def _build_record_model(
        self, variable_keys: List[str], label_map: Dict[str, str]
    ) -> Type[BaseModel]:
        """Dynamically build a Pydantic model for record data."""

        fields: Dict[str, Tuple[Optional[Any], Any]] = {}
        for key in variable_keys:
            fields[key] = (
                Optional[Any],
                Field(None, alias=key, description=label_map.get(key, key)),
            )

        return create_model("RecordData", __base__=BaseModel, **fields)  # type: ignore

    def _fetch_records(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        extra_filters: Optional[Dict[str, Union[Any, Tuple[str, Any], List[Any]]]] = None,
    ) -> List[RecordModel]:
        """Retrieve records for ``study_key`` applying optional filters."""

        filters: Dict[str, Union[Any, Tuple[str, Any], List[Any]]] = extra_filters or {}
        if visit_key is not None:
            try:
                filters["visitId"] = int(visit_key)
            except ValueError:
                logger.warning(
                    "Invalid visit_key '%s'. Should be convertible to int. Fetching all records.",
                    visit_key,
                )

        filter_str = build_filter_string(filters) if filters else None
        try:
            return self.sdk.records.list(study_key=study_key, filter=filter_str)
        except Exception as exc:  # pragma: no cover - network errors hard to simulate
            logger.error("Failed to fetch records for study '%s': %s", study_key, exc)
            return []

    def _parse_records(
        self, records: List[RecordModel], record_model: Type[BaseModel]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Parse ``records`` using ``record_model`` and count errors."""

        rows: List[Dict[str, Any]] = []
        errors = 0
        for record in records:
            try:
                metadata = {
                    "recordId": record.record_id,
                    "subjectKey": record.subject_key,
                    "visitId": record.visit_id,
                    "formId": record.form_id,
                    "recordStatus": record.record_status,
                    "dateCreated": record.date_created.isoformat() if record.date_created else None,
                }
                data_dict = record.record_data if isinstance(record.record_data, dict) else {}
                parsed = record_model(**data_dict).model_dump(by_alias=False)
                rows.append({**metadata, **parsed})
            except (ValidationError, TypeError) as exc:
                errors += 1
                logger.warning(
                    "Failed to parse record data for recordId %s: %s", record.record_id, exc
                )
            except Exception as exc:  # pragma: no cover - unexpected errors
                errors += 1
                logger.error("Unexpected error processing recordId %s: %s", record.record_id, exc)
        return rows, errors

    def _build_dataframe(
        self,
        rows: List[Dict[str, Any]],
        variable_keys: List[str],
        label_map: Dict[str, str],
        use_labels: bool,
    ) -> pd.DataFrame:
        """Construct a DataFrame from parsed record rows."""

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        meta_cols = [
            "recordId",
            "subjectKey",
            "visitId",
            "formId",
            "recordStatus",
            "dateCreated",
        ]
        for key in variable_keys:
            if key not in df.columns:
                df[key] = pd.NA
        df = df[meta_cols + variable_keys]
        if use_labels:
            rename_map = {key: label_map.get(key, key) for key in variable_keys}
            df = df.rename(columns=rename_map)
        return df
