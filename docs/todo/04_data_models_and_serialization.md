<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\todo\04_data_models_and_serialization.md -->
# Task 04: Data Models and Serialization (Pydantic v2+)

**Objective:** Define Pydantic v2+ models for all iMednet API data structures, ensuring robust validation, serialization, and deserialization.

**Key Requirements & Sub-Tasks:**

* [ ] **Define Pydantic Models for all API Structures:**
  * [ ] **Identify Task:** Create Pydantic v2+ models in `imednet_sdk/models/` for all request bodies and response structures documented in `docs/reference/`.
  * [ ] **Write/Update Tests:** Create/update `tests/models/` (e.g., `test_common_models.py`, `test_study_model.py`, etc.). For each model, add tests to:
    * [ ] Verify successful validation and deserialization from valid JSON/dict data (using examples from `docs/reference/*.md` or dedicated fixtures). Use `ModelName.model_validate(data)`.
    * [ ] Verify successful serialization to JSON/dict. Use `model_instance.model_dump(mode='json')` for JSON-compatible output or `model_instance.model_dump()` for dict. Consider `by_alias=True` if using field aliases.
    * [ ] Verify `pydantic.ValidationError` is raised for incorrect data types, missing required fields, or failed custom validation.
    * [ ] Verify correct handling of optional fields (`Optional[T]`, `| None`) and `null` values.
    * [ ] Verify custom validators (e.g., using `@field_validator` or `Annotated` types for dates, enums) work correctly.
    * [ ] Verify handling of generic models (e.g., `ApiResponseModel`). Use `pydantic.TypeAdapter` for validating lists/unions directly (e.g., `TypeAdapter(List[StudyModel]).validate_python(list_of_study_data)`).
  * [ ] **Implement Code:**
    * [ ] Ensure `imednet_sdk/models/__init__.py` exists and exports models.
    * [ ] Create/organize model files (e.g., `_common.py`, `study.py`, `site.py`, etc.).
    * [ ] **Common Models (`_common.py` - based on `docs/reference/1 common.md`, `2 header.md`, `3 error.md`):**
      * [ ] `MetadataModel`: Define fields for pagination, sorting, etc.
      * [ ] `ErrorDetailModel`: Define fields for error messages.
      * [ ] `FieldErrorModel`: Define fields for specific field errors.
      * [ ] `SortInfoModel`: Define fields for sorting parameters.
      * [ ] `PaginationInfoModel`: Define fields for pagination details (limit, offset, total).
      * [ ] `ApiResponseModel[T]`: Define a generic model using `typing.TypeVar` and `pydantic.BaseModel`, `typing.Generic` for standard API responses containing `metadata` and `data: T`.
      * [ ] `JobStatusModel` (from `docs/reference/jobs.md`): Define fields for job status responses.
    * [ ] **Resource-Specific Models (referencing corresponding `docs/reference/*.md` files):**
      * [ ] `StudyModel` (`studies.md`)
      * [ ] `SiteModel` (`sites.md`)
      * [ ] `UserModel` (`users.md`)
      * [ ] `SubjectModel` (`subjects.md`)
      * [ ] `VisitModel` (`visits.md`)
      * [ ] `FormModel` (`forms.md`)
      * [ ] `VariableModel` (`variables.md`)
      * [ ] `RecordModel` (`records.md`) - Pay attention to the dynamic `recordData: Dict[str, Any]` field. Consider validation if specific keys are known.
      * [ ] `RecordRevisionModel` (`record_revisions.md`)
      * [ ] `QueryModel` (`queries.md`)
      * [ ] `CodingModel` (`codings.md`)
      * [ ] `IntervalModel` (`intervals.md`)
      * [ ] Add any other models identified in the reference docs.
    * [ ] **Request Body Models:**
      * [ ] `RecordCreateModel` (or similar, based on `POST /records` requirements)
      * [ ] Define models for any other `POST`/`PUT`/`PATCH` request bodies identified in the API documentation.
    * [ ] **Implementation Details:**
      * [ ] Use `pydantic.BaseModel` as the base for all models.
      * [ ] Use `pydantic.Field` for aliasing (`alias='apiFieldName'`), default values, etc.
      * [ ] Use `pydantic.ConfigDict` within models for configuration (e.g., `model_config = ConfigDict(extra='ignore')` or `populate_by_name=True`).
      * [ ] Implement custom date/datetime parsing/validation using `@field_validator` or `Annotated` types with `BeforeValidator` or `AfterValidator`. Ensure conversion to standard `datetime.datetime` or `datetime.date` objects. Handle formats like `YYYY-MM-DDTHH:MM:SSZ`, `YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DD`.
      * [ ] Use standard Python types (`str`, `int`, `float`, `bool`) and `typing` module types (`Optional`, `List`, `Dict`, `Literal`, `Union`, `Any`).
  * [ ] **Run Specific Tests:** `pytest tests/models/test_specific_model.py` (or use `-k model_name`).
  * [ ] **Debug & Iterate:** Fix model definitions or tests based on `ValidationError` messages until specific tests pass.
  * [ ] **Run All Model Unit Tests:** `pytest tests/models/`
  * [ ] **Update Memory File:** Document model structure, design choices (aliases, validation), and Pydantic v2 usage in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address linting, typing, formatting.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/models/test_specific_model.py`
  * [ ] **Re-run All Model Unit Tests (Post-Fix):** `pytest tests/models/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m "feat(models): define pydantic v2 models for API structures"` (or break down commits per resource).

* [ ] **Integrate Deserialization into the Client:**
  * [ ] **Identify Task:** Modify the client's request methods (`_request`, `get`, etc.) to automatically deserialize successful JSON responses into the appropriate Pydantic models using Pydantic v2 methods.
  * [ ] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) to:
    * [ ] Verify successful requests return the correct Pydantic model instance(s) (e.g., `StudyModel`, `List[SiteModel]`, `ApiResponseModel[List[RecordModel]]`).
    * [ ] Verify that `pydantic.ValidationError` during response parsing is caught and potentially wrapped in a custom SDK exception (e.g., `DeserializationError` - see Task 06).
  * [ ] **Implement Code:**
    * [ ] Modify `_request` in `imednet_sdk/client.py`.
    * [ ] Define expected response model type (e.g., pass `response_model: Type[BaseModel]` or `Type[List[BaseModel]]` or similar to request methods).
    * [ ] After getting successful JSON (`response.json()`), use `response_model.model_validate(data)` or `TypeAdapter(response_model).validate_python(data)` for lists/unions.
    * [ ] Wrap potential `pydantic.ValidationError` in a custom exception (Task 06).
    * [ ] Return the validated Pydantic model instance(s).
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [ ] **Debug & Iterate:** Fix client code, model definitions, or tests.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document client deserialization logic using Pydantic v2 in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m "feat(client): integrate pydantic v2 deserialization"`

* [ ] **Integrate Serialization into the Client:**
  * [ ] **Identify Task:** Modify client methods (`post`, `put`, `patch`) to accept Pydantic model instances as input and serialize them correctly to JSON for the request body using Pydantic v2 methods.
  * [ ] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) for relevant methods:
    * [ ] Verify passing a Pydantic model instance as `data` or `json` parameter works.
    * [ ] Use mocking (`respx` or `unittest.mock`) to verify the correct JSON payload (generated via `model.model_dump(mode='json', by_alias=True)`) is sent. Consider `exclude_unset=True` or `exclude_none=True` based on API requirements.
  * [ ] **Implement Code:**
    * [ ] Modify methods like `post`, `put`, `patch` in `imednet_sdk/client.py`.
    * [ ] Check if the input payload argument is an instance of `pydantic.BaseModel`.
    * [ ] If it is, serialize it using `model.model_dump(mode='json', by_alias=True)` (adjust parameters like `exclude_unset`, `exclude_none` as needed).
    * [ ] Pass the resulting JSON string or dictionary (depending on `httpx` requirements) as the `content` or `json` parameter to `httpx.request`.
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [ ] **Debug & Iterate:** Fix client code or tests.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document client serialization logic using Pydantic v2 in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
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
