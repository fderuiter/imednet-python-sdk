import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, create_model

from imednet.endpoints.records import Record as RecordModel  # type: ignore[attr-defined]
from imednet.endpoints.variables import Variable as VariableModel  # type: ignore[attr-defined]

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

    def __init__(self, sdk: "ImednetSDK") -> None:
        """Initialize with an :class:`ImednetSDK` instance."""
        self.sdk = sdk

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _fetch_variable_metadata(
        self,
        study_key: str,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> Tuple[List[str], Dict[str, str]]:
        """Return variable names and label mapping for a study."""
        filters: Dict[str, Any] = {}
        if variable_whitelist is not None:
            filters["variableNames"] = variable_whitelist
        if form_whitelist is not None:
            filters["formIds"] = form_whitelist

        variables: List[VariableModel] = self.sdk.variables.list(
            study_key=study_key,
            **filters,
        )
        if not variables:
            logger.warning(
                "No variables found for study '%s'. Returning empty DataFrame.",
                study_key,
            )
            return [], {}

        variable_keys = [v.variable_name for v in variables]
        label_map = {v.variable_name: v.label for v in variables}
        return variable_keys, label_map

    def _build_record_model(
        self, variable_keys: List[str], label_map: Dict[str, str]
    ) -> Type[BaseModel]:
        """Create a dynamic model for the record data payload."""
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
        """Fetch records for a study applying optional filters."""
        filters: Dict[str, Union[Any, Tuple[str, Any], List[Any]]] = (
            dict(extra_filters) if extra_filters else {}
        )
        if visit_key is not None:
            try:
                filters["visitId"] = int(visit_key)
            except ValueError:
                logger.warning(
                    "Invalid visit_key '%s'. Should be convertible to int. Fetching all records.",
                    visit_key,
                )
        try:
            return self.sdk.records.list(
                study_key=study_key,
                record_data_filter=None,
                **filters,
            )
        except Exception as exc:  # pragma: no cover - unexpected
            logger.error("Failed to fetch records for study '%s': %s", study_key, exc)
            return []

    def _parse_records(
        self, records: List[RecordModel], record_model: Type[BaseModel]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Parse raw records into row dictionaries and count failures."""
        rows: List[Dict[str, Any]] = []
        errors = 0
        for rec in records:
            try:
                meta = {
                    "recordId": rec.record_id,
                    "subjectKey": rec.subject_key,
                    "visitId": rec.visit_id,
                    "formId": rec.form_id,
                    "recordStatus": rec.record_status,
                    "dateCreated": rec.date_created.isoformat() if rec.date_created else None,
                }
                data = rec.record_data if isinstance(rec.record_data, dict) else {}
                parsed = record_model(**data).model_dump(by_alias=False)
                rows.append({**meta, **parsed})
            except (ValidationError, TypeError) as exc:
                errors += 1
                logger.warning(
                    "Failed to parse record data for recordId %s: %s",
                    rec.record_id,
                    exc,
                )
            except Exception as exc:  # pragma: no cover - unexpected
                errors += 1
                logger.error("Unexpected error processing recordId %s: %s", rec.record_id, exc)
        return rows, errors

    def _build_dataframe(
        self,
        rows: List[Dict[str, Any]],
        variable_keys: List[str],
        label_map: Dict[str, str],
        use_labels: bool,
    ) -> pd.DataFrame:
        """Create the output DataFrame from parsed rows."""
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

    def dataframe(
        self,
        study_key: str,
        visit_key: Optional[str] = None,
        use_labels_as_columns: bool = True,
        variable_whitelist: Optional[List[str]] = None,
        form_whitelist: Optional[List[int]] = None,
    ) -> pd.DataFrame:
        """Return a :class:`pandas.DataFrame` of records for a study."""
        variable_keys, label_map = self._fetch_variable_metadata(
            study_key,
            variable_whitelist=variable_whitelist,
            form_whitelist=form_whitelist,
        )
        if not variable_keys:
            return pd.DataFrame()

        record_model = self._build_record_model(variable_keys, label_map)
        extra_filters: Dict[str, Any] = {}
        if variable_whitelist is not None:
            extra_filters["variableNames"] = variable_whitelist
        if form_whitelist is not None:
            extra_filters["formIds"] = form_whitelist

        records = self._fetch_records(
            study_key,
            visit_key,
            extra_filters=extra_filters or None,
        )
        rows, errors = self._parse_records(records, record_model)
        if errors:
            logger.warning("Encountered %s errors while parsing record data.", errors)

        df = self._build_dataframe(rows, variable_keys, label_map, use_labels_as_columns)
        if df.empty:
            logger.info(
                "No records processed successfully for study '%s' with the given filters.",
                study_key,
            )
        return df
