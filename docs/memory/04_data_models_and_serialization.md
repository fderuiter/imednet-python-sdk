<!-- filepath: /Users/fred/Documents/GitHub/imednet-python-sdk/docs/memory/04_data_models_and_serialization.md -->
# Memory: Task 04 - Data Models and Serialization

**Date:** 2025-04-18

**Context:** This task focused on defining Pydantic v2+ models for all iMednet API data structures (requests and responses) and integrating them into the `ImednetClient`.

**Key Decisions & Implementations:**

1. **Pydantic v2+:** Adopted Pydantic v2 for all data modeling due to its performance improvements and enhanced features.
2. **Model Location:** All models are located within the `imednet_sdk/models/` directory, organized by resource (e.g., `study.py`, `record.py`) with common models in `_common.py`.
3. **Model Definitions:**
    * Created models for all documented GET response structures found in `docs/reference/`.
    * Used `pydantic.Field` extensively for aliasing (`alias='apiFieldName'`) to map between Python snake_case and API camelCase.
    * Handled optional fields using `typing.Optional` or `| None`.
    * Implemented date/datetime parsing using Pydantic's built-in capabilities, assuming ISO 8601 or similar formats parsable by default. Added custom validators where necessary (though default parsing covered most cases found).
    * Defined a generic `ApiResponse[T]` model in `_common.py` using `typing.TypeVar` and `typing.Generic` to represent the standard `{metadata: ..., data: ...}` structure.
    * Created `RecordPostItem` model specifically for the items within the list body of the `POST /records` request, based on `docs/reference/records.md`.
4. **Client Integration:**
    * Modified `ImednetClient._request` to accept an optional `response_model` parameter.
    * Used `pydantic.TypeAdapter` within `_request` to handle deserialization of both single models (`ModelType`) and lists (`List[ModelType]`) based on the `response_model` provided.
    * Implemented basic error handling for `JSONDecodeError` (via `ValueError`) and `pydantic.ValidationError` during response processing, raising `RuntimeError` for now (to be replaced by custom exceptions in Task 06).
    * Modified `_request` to automatically serialize Pydantic `BaseModel` instances passed to the `json` parameter using `model.model_dump(mode='json', by_alias=True)`.
    * Updated helper methods (`_get`, `_post`) to accept `response_model` and pass Pydantic models directly to `_request`.
5. **Testing:**
    * Added comprehensive unit tests for each model in `tests/models/`, covering validation, serialization, aliases, optional fields, and error conditions.
    * Added tests in `tests/test_client.py` specifically verifying the client's ability to serialize request models and deserialize response models (including single objects, lists, and error handling).
    * Used `pydantic.TypeAdapter` in tests for `ApiResponse` (`test_common_models.py`) to validate generic model handling.

**Open Issues/Next Steps (Related to this task):**

* Refine error handling in `_request` to use custom SDK exceptions (Task 06).
* Complete pre-commit checks and fix any remaining issues.
* Commit the finalized changes for Task 04.
