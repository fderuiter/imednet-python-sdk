"""Utility functions for the iMednet SDK.

This module provides helper functions used across the SDK, primarily for
handling dynamic data structures based on API metadata. Key functions include:

- `build_model_from_variables`: Dynamically creates Pydantic models from
  iMednet variable definitions.
- `_fetch_and_parse_typed_records`: Fetches form variables and records, then
  parses record data into dynamically typed models (used by `ImednetClient.get_typed_records`).
"""

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

# Import BaseModel directly from pydantic
from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from .exceptions import ImednetSdkException

if TYPE_CHECKING:
    from .api._base import ResourceClient
    from .models import RecordModel, VariableModel

logger = logging.getLogger(__name__)

# 1. map iMednet types → (Python type, Pydantic Field args if any)
# Needs refinement based on actual API date formats and validation needs
# Using Optional[...] for all fields initially, assuming data might be missing.
TYPE_MAP: Dict[str, Tuple[Type, Dict[str, Any]]] = {
    """Maps iMednet variableType strings to Python types and Pydantic Field arguments.

    Used by `build_model_from_variables` to dynamically create Pydantic models
    representing recordData based on form variable definitions.
    Types are initially Optional to handle potentially missing data.
    """
    "textField": (Optional[str], {}),
    "numberField": (Optional[float], {}),
    "integerField": (Optional[int], {}),
    "dateField": (Optional[date], {}),  # TODO: Add validator if format isn't ISO
    "dateTimeField": (Optional[datetime], {}),  # TODO: Add validator if format isn't ISO
    "checkboxField": (Optional[bool], {}),  # Assuming API returns true/false or 0/1
    "radioField": (Optional[str], {}),  # Could potentially be Enum if choices are known
    "dropdownField": (Optional[str], {}),  # Could potentially be Enum if choices are known
    "textAreaField": (Optional[str], {}),
    # Add other known types from docs/reference/variables.md if necessary
    # Default to Optional[Any] for unknown types for flexibility
    "unknown": (Optional[Any], {}),
}


def build_model_from_variables(vars_meta: List[Dict[str, Any]], model_name: str) -> Type[BaseModel]:
    """Dynamically creates a Pydantic model from iMednet variable metadata.

    Constructs a Pydantic `BaseModel` subclass where fields correspond to the
    `variableName` from the metadata, and types are mapped from `variableType`
    using the `TYPE_MAP`.

    Args:
        vars_meta: A list of dictionaries, where each dictionary represents
                   variable metadata obtained from the iMednet API (e.g., via
                   the `/variables` endpoint). Each dictionary must contain
                   at least 'variableName' and 'variableType' keys.
        model_name: The desired class name for the dynamically created Pydantic model.
                   This name should be unique and descriptive (e.g., "MyFormRecordData").

    Returns:
        A new Pydantic `BaseModel` class definition.

    Raises:
        ValueError: If any dictionary in `vars_meta` lacks the 'variableName' key.
    """
    fields: Dict[str, Tuple[Type, Any]] = {}
    for var in vars_meta:
        # Use variableType from the model, default to 'unknown' if missing
        field_type_str = var.get("variableType", "unknown")
        py_type, field_args = TYPE_MAP.get(field_type_str, TYPE_MAP["unknown"])

        # Use variableName as the Python field name
        field_name = var.get("variableName")
        if not field_name:
            # Log or raise? Raising is safer to indicate bad metadata.
            raise ValueError(f"Variable metadata missing 'variableName': {var}")

        # Pydantic needs (Type, default_value) or (Type, Field(...))
        # We use Field() to set default=None for Optional types and allow future extension
        # Use alias if the variableName is not a valid Python identifier, though unlikely
        # For simplicity, directly using variableName as field name.
        fields[field_name] = (py_type, Field(default=None, **field_args))

    # Create the model with extra='ignore' to handle potential extra fields in recordData
    DynamicRecordModel = create_model(
        model_name, __config__=ConfigDict(extra="ignore"), **fields
    )  # type: ignore[call-overload]
    return DynamicRecordModel


def _fetch_and_parse_typed_records(
    variables_client: "ResourceClient",  # Use forward reference
    records_client: "ResourceClient",  # Use forward reference
    study_key: str,
    form_key: str,
    **kwargs,
) -> List[BaseModel]:
    """Fetches variables, builds a model, fetches records, and parses recordData.

    This internal helper function orchestrates the process of getting dynamically
    typed record data for a specific form.

    Steps:
    1. Fetches all variables for the given `study_key` and `form_key` using
       `variables_client.list()`.
    2. Builds a dynamic Pydantic model using `build_model_from_variables` based
       on the fetched variable metadata.
    3. Fetches all records for the `study_key` and `form_key` using
       `records_client.list()`, passing through any additional `kwargs`.
    4. Parses the `recordData` dictionary from each fetched record using the
       dynamically created model.
    5. Logs warnings for records where `recordData` fails validation against the model.

    Args:
        variables_client: An initialized `VariablesClient` instance.
        records_client: An initialized `RecordsClient` instance.
        study_key: The key identifying the study.
        form_key: The key identifying the form.
        **kwargs: Additional keyword arguments to pass directly to the
                  `records_client.list()` method (e.g., `filter`, `sort`, `size`).

    Returns:
        A list of Pydantic model instances, where each instance represents the
        validated `recordData` of a fetched record. Records with invalid data
        are excluded, and warnings are logged.

    Raises:
        ImednetSdkException: If fetching variables or records from the API fails.
        ValueError: If building the dynamic model fails (e.g., missing 'variableName'
                    in variable metadata).
    """
    # Import models inside the function to break the circular dependency
    from .models import RecordModel, VariableModel

    # 1) Fetch variable metadata
    try:
        variables_response = variables_client.list_variables(
            study_key, filter=f"formKey=={form_key}"
        )
        vars_meta: List[VariableModel] = variables_response.data
        if not vars_meta:
            logger.warning(
                f"No variables found for study '{study_key}', form '{form_key}'. "
                f"Cannot create typed model. Returning empty list."
            )
            return []
    except ImednetSdkException as e:
        logger.error(f"Failed to fetch variables for study '{study_key}', form '{form_key}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching variables for form '{form_key}': {e}")
        raise ImednetSdkException(f"Unexpected error fetching variables: {e}") from e

    vars_meta_dict = [v.model_dump(by_alias=False) for v in vars_meta]

    # 2) Build dynamic Record model
    model_name = f"{form_key.replace(' ', '_').capitalize()}RecordData"
    try:
        DynamicRecordDataModel = build_model_from_variables(vars_meta_dict, model_name=model_name)
    except ValueError as e:
        logger.error(f"Failed to build dynamic model '{model_name}' for form '{form_key}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error building dynamic model for form '{form_key}': {e}")
        raise ImednetSdkException(f"Unexpected error building dynamic model: {e}") from e

    # 3) Fetch raw records
    typed_records: List[BaseModel] = []
    try:
        existing_filter = kwargs.pop("filter", None)
        combined_filter = f"formKey=={form_key}"
        if existing_filter:
            combined_filter = f"({existing_filter}) and {combined_filter}"

        records_response = records_client.list_records(study_key, filter=combined_filter, **kwargs)
        raw_records: List[RecordModel] = records_response.data

        # 4) Parse each recordData
        for record in raw_records:
            record_data_dict = record.recordData or {}
            try:
                typed_data_instance = DynamicRecordDataModel.model_validate(record_data_dict)
                typed_records.append(typed_data_instance)
            except ValidationError as e:
                logger.warning(
                    f"Skipping record {record.recordId} (Subject: {record.subjectKey}) in form "
                    f"'{form_key}' due to validation error: {e}"
                )
            except Exception as e:
                logger.warning(
                    f"Skipping record {record.recordId} (Subject: {record.subjectKey}) in form "
                    f"'{form_key}' due to unexpected parsing error: {e}"
                )

    except ImednetSdkException as e:
        logger.error(
            f"Failed to fetch or parse records for study '{study_key}', form '{form_key}': {e}"
        )
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching/parsing records for form '{form_key}': {e}")
        raise ImednetSdkException(f"Unexpected error fetching/parsing records: {e}") from e

    return typed_records
