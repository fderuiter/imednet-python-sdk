# Task 07: Dynamic Record Typing (`get_typed_records`)

**Objective:** Implement a method that fetches records and dynamically parses their `recordData` into typed Pydantic models based on variable metadata fetched from the API for a specific form.

**Definition of Done:**

* A method exists in the `VariablesClient` (e.g., `list_variables`) to fetch variable metadata for a specific form key within a study.
* A helper function (e.g., `build_model_from_variables` in `utils.py`) exists to dynamically create a Pydantic model using `pydantic.create_model` based on the variable metadata (name, fieldType).
* A mapping (`TYPE_MAP`) from iMednet `fieldType` strings to Python types (and potentially default values or validators) is defined and used by the model builder.
* A high-level method (e.g., `get_typed_records` in `ImednetClient` or `RecordsClient`) orchestrates the process:
  * Calls the variables endpoint to get metadata for the given `study_key` and `form_key`.
  * Calls the helper function to build the dynamic Pydantic model.
  * Calls the records endpoint (e.g., `list_records` or potentially an iterator from Task 10) to get raw record data for the `study_key` and `form_key`.
  * Iterates through the raw records, attempting to parse the `recordData` dictionary of each record using the dynamically created model.
  * Handles potential `pydantic.ValidationError` or missing `recordData` gracefully (e.g., logging, skipping).
* The `get_typed_records` method returns a list of validated, dynamically-typed Pydantic model instances representing the `recordData`.
* Unit tests exist for the `build_model_from_variables` helper function.
* Unit tests exist for the `get_typed_records` method, mocking API calls for both variables and records, and verifying successful parsing and error handling.
* Documentation (Task 8) and examples (Task 8) are updated to demonstrate the usage of `get_typed_records`.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., implement `build_model_from_variables`).
2. **Write/Update Tests (TDD):**
    * For the model builder: Write tests in `tests/test_utils.py` (or similar) that provide sample variable metadata and assert the correct Pydantic model is created.
    * For `get_typed_records`: Write tests in the relevant client test file (e.g., `tests/test_client.py` or `tests/api/test_records.py`). Mock `list_variables` and `list_records` calls. Provide mock variable metadata and record data. Assert that the correct typed objects are returned and that parsing errors are handled.
3. **Implement Code:**
    * Implement the `list_variables` method in `imednet_sdk/api/variables.py` (if not already done).
    * Define the `TYPE_MAP` in `imednet_sdk/utils.py` or a dedicated constants file.
    * Implement the `build_model_from_variables` function in `imednet_sdk/utils.py`.
    * Implement the `get_typed_records` method in the chosen client class.
    * Integrate the calls and parsing logic.
4. **Run Specific Tests:** Execute the tests written in step 2.
5. **Debug & Iterate:** Fix implementation or tests until specific tests pass.
6. **Run All Applicable Tests:** Run the full test suite (`pytest tests/`) to check for regressions.
7. **Update Memory File:** Document the implementation details, design choices (e.g., location of methods, error handling strategy), and test results in `docs/memory/12_dynamic_record_typing.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`.
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Tests (Post-Fix):** Verify fixes (Step 4).
12. **Re-run All Applicable Checks (Post-Fix - Optional):** Verify overall integrity (Step 6).
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/12_dynamic_record_typing.md`
16. **Commit Changes:** `git commit -m "feat(core): implement dynamic record typing"` (Adjust type/scope and message per sub-task).

**Sub-Tasks:**

* [ ] **Implement `VariablesClient.list_variables`:**
  * Ensure it accepts `study_key` and `form_key` (and potentially other filters/pagination from `variables.md`).
  * Ensure it returns `List[VariableModel]`.
  * Add corresponding unit tests.
* [ ] **Define `TYPE_MAP`:**
  * Create a dictionary mapping iMednet `fieldType` strings to Python types (e.g., `str`, `int`, `float`, `bool`, `datetime.date`, `datetime.datetime`). Consider using `Annotated` or validators for date parsing.
  * Place it in `imednet_sdk/utils.py` or similar.
* [ ] **Implement `build_model_from_variables`:**
  * Create function in `imednet_sdk/utils.py`.
  * Takes variable metadata (`List[VariableModel]` or `List[Dict]`) and a `model_name` string.
  * Uses `TYPE_MAP` and `pydantic.create_model` to generate a `BaseModel` subclass.
  * Add unit tests in `tests/test_utils.py`.
* [ ] **Implement `get_typed_records` Method:**
  * Decide location (e.g., `ImednetClient` or `RecordsClient`).
  * Implement the orchestration logic: call variables, build model, call records, parse data.
  * Handle `recordData` parsing errors (e.g., `try...except ValidationError`).
  * Return `List[BaseModel]` (where `BaseModel` is the dynamically created type).
* [ ] **Implement Unit Tests for `get_typed_records`:**
  * Mock `list_variables` and `list_records` (or iterator).
  * Test successful parsing for various data types.
  * Test handling of missing `recordData`.
  * Test handling of `ValidationError` during parsing.
* [ ] **Update Documentation & Examples (Task 8):**
  * Add a section to `usage.rst` explaining how to use `get_typed_records`.
  * Create a new example script in `examples/` demonstrating its use.
  * Ensure the method has a clear docstring.

**Code Sketch:**

```python
# --- In imednet_sdk/utils.py ---
from pydantic import BaseModel, create_model, Field, field_validator
from typing import Any, Dict, List, Tuple, Type, Optional
from datetime import date, datetime

# 1. map iMednet types → (Python type, Pydantic Field args if any)
# Needs refinement based on actual API date formats and validation needs
TYPE_MAP: Dict[str, Tuple[Type, Dict[str, Any]]] = {
    "textField":     (Optional[str], {}),
    "numberField":   (Optional[float], {}),
    "integerField":  (Optional[int], {}),
    "dateField":     (Optional[date], {}), # Requires validator or Annotated
    "dateTimeField": (Optional[datetime], {}), # Requires validator or Annotated
    "checkboxField": (Optional[bool], {}),
    "radioField":    (Optional[str], {}), # Or maybe Enum if possible?
    "dropdownField": (Optional[str], {}), # Or maybe Enum?
    "textAreaField": (Optional[str], {}),
    # Add other types as needed...
    # Default to Optional[Any] or raise error for unknown types?
}

def build_model_from_variables(vars_meta: List[Dict[str, Any]], model_name: str) -> Type[BaseModel]:
    """Dynamically creates a Pydantic model from variable metadata."""
    fields: Dict[str, Tuple[Type, Any]] = {}
    for var in vars_meta:
        field_type_str = var.get("fieldType", "textField") # Default or handle missing
        py_type, field_args = TYPE_MAP.get(field_type_str, (Optional[Any], {}))

        # Use variableName as the Python field name
        # Use Field(..., alias=...) if API names differ or need validation
        field_name = var.get("variableName")
        if not field_name:
            # Handle missing variableName
            continue

        # Pydantic needs (Type, default_value)
        # We use Field() to potentially add alias or validation later
        fields[field_name] = (py_type, Field(default=None, **field_args))

    # Consider adding model_config = ConfigDict(extra='ignore')
    DynamicRecordModel = create_model(model_name, **fields) # type: ignore
    return DynamicRecordModel

# --- In imednet_sdk/client.py or api/records.py ---
from .utils import build_model_from_variables
# from .api.variables import VariablesClient # Assuming structure
# from .api.records import RecordsClient # Assuming structure
from .models import VariableModel, RecordModel # Assuming base RecordModel exists
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class ImednetClient:
    # ... existing __init__, _request, properties for resource clients ...

    # Assuming resource clients are properties like self.variables, self.records
    # And they have list_variables, list_records methods

    def get_typed_records(self, study_key: str, form_key: str, **kwargs) -> List[BaseModel]:
        """
        Fetches records for a form and parses recordData into dynamically typed objects.

        Args:
            study_key: The study key.
            form_key: The form key.
            **kwargs: Additional parameters passed to the underlying list_records call
                      (e.g., filter, sort, size).

        Returns:
            A list of dynamically created Pydantic model instances, each representing
            the recordData of a fetched record.
        """
        # 1) Fetch variable metadata
        # Assuming list_variables handles pagination/fetching all if needed,
        # or we use an iterator from Task 10. For simplicity, assume it returns all.
        try:
            # Pass formKey filter to list_variables
            variables_response = self.variables.list_variables(study_key, filter=f"formKey=={form_key}")
            vars_meta: List[VariableModel] = variables_response.data
            if not vars_meta:
                logger.warning(f"No variables found for study '{study_key}', form '{form_key}'. Cannot create typed model.")
                return []
        except Exception as e:
            logger.error(f"Failed to fetch variables for form '{form_key}': {e}")
            # Re-raise or return empty list? Depends on desired behavior.
            raise # Or return []

        # Convert VariableModel list to Dict list if needed by builder
        vars_meta_dict = [v.model_dump() for v in vars_meta]

        # 2) Build a dynamic Record model
        try:
            DynamicRecordDataModel = build_model_from_variables(vars_meta_dict, model_name=f"{form_key}RecordData")
        except Exception as e:
            logger.error(f"Failed to build dynamic model for form '{form_key}': {e}")
            raise # Or return []

        # 3) Fetch raw records
        # Assuming list_records or an iterator handles pagination.
        # Pass formKey filter and any other kwargs.
        typed_records: List[BaseModel] = []
        try:
            # Use iterator if available (Task 10)
            # for record in self.records.iter_records(study_key, formKey=form_key, **kwargs):
            # Simplified: assume list_records fetches all for now
            records_response = self.records.list_records(study_key, filter=f"formKey=={form_key}", **kwargs)
            raw_records: List[RecordModel] = records_response.data

            # 4) Parse each recordData into the dynamic model
            for record in raw_records:
                record_data = record.record_data or {} # Use the parsed dict
                try:
                    # Validate the dictionary against the dynamic model
                    typed_data_instance = DynamicRecordDataModel.model_validate(record_data)
                    # How to combine base RecordModel fields with dynamic ones?
                    # Option 1: Return only the dynamic part
                    # typed_records.append(typed_data_instance)
                    # Option 2: Create a new combined model or attach dynamic part?
                    # For now, let's just return the dynamic part.
                    # Consider adding recordId or other base fields if useful.
                    # setattr(typed_data_instance, 'record_id', record.record_id) # Example
                    typed_records.append(typed_data_instance)

                except ValidationError as e:
                    logger.warning(f"Skipping record {record.record_id} due to parsing error: {e}")
                except Exception as e:
                    logger.warning(f"Skipping record {record.record_id} due to unexpected error: {e}")

        except Exception as e:
            logger.error(f"Failed to fetch or parse records for form '{form_key}': {e}")
            raise # Or return typed_records collected so far?

        return typed_records

```
