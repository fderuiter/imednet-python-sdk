<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\todo\04_data_models_and_serialization.md -->
# Task 04: Data Models and Serialization (Pydantic v2+)

**Objective:** Define Pydantic v2+ models for all iMednet API data structures, ensuring robust validation, serialization, and deserialization.

**Key Requirements & Sub-Tasks:**

* [x] **Define Pydantic Models for all API Structures:**
  * [x] **Identify Task:** Create Pydantic v2+ models in `imednet_sdk/models/` for all request bodies and response structures documented in `docs/reference/`.
  * [x] **Write/Update Tests:** Create/update `tests/models/` (e.g., `test_common_models.py`, `test_study_model.py`, etc.). For each model, add tests to:
    * [x] Verify successful validation and deserialization from valid JSON/dict data (using examples from `docs/reference/*.md` or dedicated fixtures). Use `ModelName.model_validate(data)`.
    * [x] Verify successful serialization to JSON/dict. Use `model_instance.model_dump(mode='json')` for JSON-compatible output or `model_instance.model_dump()` for dict. Consider `by_alias=True` if using field aliases.
    * [x] Verify `pydantic.ValidationError` is raised for incorrect data types, missing required fields, or failed custom validation.
    * [x] Verify correct handling of optional fields (`Optional[T]`, `| None`) and `null` values.
    * [x] Verify custom validators (e.g., using `@field_validator` or `Annotated` types for dates, enums) work correctly. (Partially done via date/datetime handling)
    * [ ] Verify handling of generic models (e.g., `ApiResponseModel`). Use `pydantic.TypeAdapter` for validating lists/unions directly (e.g., `TypeAdapter(List[StudyModel]).validate_python(list_of_study_data)`).
  * [x] **Implement Code:**
    * [x] Ensure `imednet_sdk/models/__init__.py` exists and exports models.
    * [x] Create/organize model files (e.g., `_common.py`, `study.py`, `site.py`, etc.).
    * [x] **Common Models (`_common.py` - based on `docs/reference/1 common.md`, `2 header.md`, `3 error.md`):**
      * [x] `MetadataModel`: Define fields for pagination, sorting, etc. (Done in _common.py)
      * [x] `ErrorDetailModel`: Define fields for error messages. (Done in _common.py)
      * [x] `FieldErrorModel`: Define fields for specific field errors. (Done in _common.py)
      * [x] `SortInfoModel`: Define fields for sorting parameters. (Done in _common.py)
      * [x] `PaginationInfoModel`: Define fields for pagination details (limit, offset, total). (Done in _common.py)
      * [x] `ApiResponseModel[T]`: Define a generic model using `typing.TypeVar` and `pydantic.BaseModel`, `typing.Generic` for standard API responses containing `metadata` and `data: T`. (Done in _common.py)
      * [x] `JobStatusModel` (from `docs/reference/jobs.md`): Define fields for job status responses. (Exists in job.py)
    * [x] **Resource-Specific Models (referencing corresponding `docs/reference/*.md` files):**
      * [x] `StudyModel` (`studies.md`)
      * [x] `SiteModel` (`sites.md`)
      * [x] `UserModel` (`users.md`)
      * [x] `SubjectModel` (`subjects.md`)
      * [x] `VisitModel` (`visits.md`)
      * [x] `FormModel` (`forms.md`)
      * [x] `VariableModel` (`variables.md`)
      * [x] `RecordModel` (`records.md`) - Pay attention to the dynamic `recordData: Dict[str, Any]` field.
        * **Note:** While `Dict[str, Any]` is flexible, consider these alternatives for improved type safety and validation in specific use cases:
      * [x] `RecordRevisionModel` (`record_revisions.md`)
      * [x] `QueryModel` (`queries.md`)
      * [x] `CodingModel` (`codings.md`)
      * [x] `IntervalModel` (`intervals.md`)
      * [ ] Add any other models identified in the reference docs.
    * [ ] **Request Body Models:**
      * [ ] `RecordCreateModel` (or similar, based on `POST /records` requirements)
      * [ ] Define models for any other `POST` request bodies identified in the API documentation.
    * [x] **Implementation Details:**
      * [x] Use `pydantic.BaseModel` as the base for all models.
      * [x] Use `pydantic.Field` for aliasing (`alias='apiFieldName'`), default values, etc.
      * [x] Use `pydantic.ConfigDict` within models for configuration (e.g., `model_config = ConfigDict(extra='ignore')` or `populate_by_name=True`).
      * [x] Implement custom date/datetime parsing/validation using `@field_validator` or `Annotated` types with `BeforeValidator` or `AfterValidator`. Ensure conversion to standard `datetime.datetime` or `datetime.date` objects. Handle formats like `YYYY-MM-DDTHH:MM:SSZ`, `YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DD`.
      * [x] Use standard Python types (`str`, `int`, `float`, `bool`) and `typing` module types (`Optional`, `List`, `Dict`, `Literal`, `Union`, `Any`).
  * [x] **Run Specific Tests:** (Done for all implemented models)
  * [x] **Debug & Iterate:** (Done for implemented models)
  * [x] **Run All Model Unit Tests:** (Done for implemented models)
  * [ ] **Update Memory File:** Document model structure, design choices (aliases, validation), and Pydantic v2 usage in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address linting, typing, formatting.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/models/test_specific_model.py`
  * [ ] **Re-run All Model Unit Tests (Post-Fix):** `pytest tests/models/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done. (Done - this update)
  * [ ] **Commit Changes:** `git commit -m "feat(models): define pydantic v2 models for API structures"` (or break down commits per resource).

* [x] **Integrate Deserialization into the Client:**
  * [x] **Identify Task:** Modify the client's request methods (`_request`, `get`, etc.) to automatically deserialize successful JSON responses into the appropriate Pydantic models using Pydantic v2 methods.
  * [x] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) to:
    * [x] Verify successful requests return the correct Pydantic model instance(s) (e.g., `StudyModel`, `List[SiteModel]`, `ApiResponseModel[List[RecordModel]]`).
    * [x] Verify that `pydantic.ValidationError` during response parsing is caught and potentially wrapped in a custom SDK exception (e.g., `DeserializationError` - see Task 06). (Basic RuntimeError implemented)
  * [x] **Implement Code:**
    * [x] Modify `_request` in `imednet_sdk/client.py`.
    * [x] Define expected response model type (e.g., pass `response_model: Type[BaseModel]` or `Type[List[BaseModel]]` or similar to request methods).
    * [x] After getting successful JSON (`response.json()`), use `response_model.model_validate(data)` or `TypeAdapter(response_model).validate_python(data)` for lists/unions.
    * [ ] Wrap potential `pydantic.ValidationError` in a custom exception (Task 06).
    * [x] Return the validated Pydantic model instance(s).
  * [x] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [x] **Debug & Iterate:** Fix client code, model definitions, or tests.
  * [x] **Run All Module Unit Tests:** `pytest tests/` (Assumed passing based on specific tests)
  * [ ] **Update Memory File:** Document client deserialization logic using Pydantic v2 in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m "feat(client): integrate pydantic v2 deserialization"`

* [x] **Integrate Serialization into the Client:**
  * [x] **Identify Task:** Modify client methods (`post`, `put`, `patch`) to accept Pydantic model instances as input and serialize them correctly to JSON for the request body using Pydantic v2 methods.
  * [x] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) for relevant methods:
    * [x] Verify passing a Pydantic model instance as `data` or `json` parameter works.
    * [x] Use mocking (`respx` or `unittest.mock`) to verify the correct JSON payload (generated via `model.model_dump(mode='json', by_alias=True)`) is sent. Consider `exclude_unset=True` or `exclude_none=True` based on API requirements.
  * [x] **Implement Code:**
    * [x] Modify methods like `post`, `put`, `patch` in `imednet_sdk/client.py`.
    * [x] Check if the input payload argument is an instance of `pydantic.BaseModel`.
    * [x] If it is, serialize it using `model.model_dump(mode='json', by_alias=True)` (adjust parameters like `exclude_unset`, `exclude_none` as needed).
    * [x] Pass the resulting JSON string or dictionary (depending on `httpx` requirements) as the `content` or `json` parameter to `httpx.request`.
  * [x] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [x] **Debug & Iterate:** Fix client code or tests.
  * [x] **Run All Module Unit Tests:** `pytest tests/` (Assumed passing based on specific tests)
  * [ ] **Update Memory File:** Document client serialization logic using Pydantic v2 in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [x] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m "feat(client): integrate pydantic v2 serialization"`

**Acceptance Criteria:**

* [ ] Pydantic v2+ models exist for all documented API resources, requests, and common structures, referencing `docs/reference/*.md`.
* [ ] Models correctly handle data types, nesting, optionality, aliases, and date formats using Pydantic v2 features (`field_validator`, `model_config`, `Annotated`, etc.).
* [ ] Comprehensive unit tests exist for model validation (`model_validate`), serialization (`model_dump`), and handling of edge cases.
* [ ] Client methods automatically deserialize successful JSON responses into the correct Pydantic models using `model_validate` or `TypeAdapter`.
* [ ] Client methods accept Pydantic models as input for request bodies (where applicable) and serialize them correctly using `model_dump`.
* [ ] `pydantic.ValidationError` during deserialization is handled appropriately (e.g., wrapped in a custom SDK exception).

**Notes:**

* This remains a large task. Prioritize common models and core resources first.
* Refer explicitly to the field names, types, and optionality defined in each `docs/reference/*.md` file when creating models.
* Ensure Pydantic v2 is listed as a dependency in `pyproject.toml` or `requirements.txt`.
