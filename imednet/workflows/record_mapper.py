import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, create_model

from imednet.endpoints.records import Record as RecordModel
from imednet.endpoints.variables import Variable as VariableModel
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
        """
        Fetches variables and records for a study and returns a DataFrame.

        :param study_key: unique identifier for the study
        :param visit_key: optional visit key to filter records (server-side)
        :param use_labels_as_columns: If True, rename columns to variable labels.
                                      If False, use variable names.
        :return: pandas DataFrame with metadata columns + one column per variable
        """
        # 1. Fetch all variable metadata for the study
        vars_all: List[VariableModel] = self.sdk.variables.list(study_key=study_key)
        if not vars_all:
            logger.warning(
                f"No variables found for study '{study_key}'. Returning empty DataFrame."
            )
            return pd.DataFrame()

        variable_keys = [v.variable_name for v in vars_all]
        label_map: Dict[str, str] = {v.variable_name: v.label for v in vars_all}

        # 2. Build dynamic Pydantic model for recordData with type hints (simplified)
        fields: Dict[str, tuple] = {}
        for key in variable_keys:
            # Use Any type for variable values
            python_type = Any
            fields[key] = (
                Optional[python_type],
                Field(None, alias=key, description=label_map.get(key, key)),
            )  # Use get for safety

        RecordDataModel: Type[BaseModel] = create_model(
            "RecordData",
            __base__=BaseModel,
            **fields,  # type: ignore
        )

        # 3. Fetch records for the study with server-side filtering
        record_filter_dict: Dict[str, Union[Any, Tuple[str, Any], List[Any]]] = {}
        if visit_key is not None:
            # Assuming visit_key corresponds to visit_id which is an int in the model
            # If visit_key can be something else, adjust filter key accordingly
            try:
                record_filter_dict["visitId"] = int(visit_key)
            except ValueError:
                logger.warning(
                    f"Invalid visit_key '{visit_key}'. "
                    "Should be convertible to int. "
                    "Fetching all records."
                )

        filter_str = build_filter_string(record_filter_dict) if record_filter_dict else None

        try:
            recs_all: List[RecordModel] = self.sdk.records.list(
                study_key=study_key, filter=filter_str
            )
        except Exception as e:
            logger.error(f"Failed to fetch records for study '{study_key}': {e}")
            return pd.DataFrame()  # Return empty on fetch failure

        # 4. Parse each record with error handling
        rows: List[Dict[str, Any]] = []
        parsing_errors = 0
        for r in recs_all:
            try:
                # Metadata fields
                meta = {
                    "recordId": r.record_id,
                    "subjectKey": r.subject_key,
                    "visitId": r.visit_id,
                    "formId": r.form_id,
                    "recordStatus": r.record_status,
                    # Ensure datetime is timezone-aware if possible, or handle appropriately
                    "dateCreated": r.date_created.isoformat() if r.date_created else None,
                }
                # Parse recordData through dynamic model
                # Ensure record_data is a dict before attempting to parse
                record_data_dict = r.record_data if isinstance(r.record_data, dict) else {}
                parsed_data = RecordDataModel(**record_data_dict).model_dump(by_alias=False)
                rows.append({**meta, **parsed_data})
            except (ValidationError, TypeError) as e:
                parsing_errors += 1
                logger.warning(f"Failed to parse record data for recordId {r.record_id}: {e}")
            except Exception as e:
                parsing_errors += 1
                logger.error(f"Unexpected error processing recordId {r.record_id}: {e}")

        if parsing_errors > 0:
            logger.warning(f"Encountered {parsing_errors} errors while parsing record data.")

        # 5. Build DataFrame
        df = pd.DataFrame(rows)
        if df.empty:
            logger.info(
                f"No records processed successfully for study '{study_key}' with the given filters."
            )
            return df

        # 6. Reorder columns: metadata first, then variables
        meta_cols = ["recordId", "subjectKey", "visitId", "formId", "recordStatus", "dateCreated"]
        # Ensure all expected variable keys are present, add missing ones with NaN
        for key in variable_keys:
            if key not in df.columns:
                df[key] = pd.NA
        # Ensure all meta columns are present
        final_cols = meta_cols + variable_keys
        df = df[final_cols]

        # 7. Rename variable columns if requested
        if use_labels_as_columns:
            rename_map = {key: label_map.get(key, key) for key in variable_keys}
            df = df.rename(columns=rename_map)

        return df
