# Task 04: Data Models and Serialization
<!-- filepath: c:\\Users\\FrederickdeRuiter\\Documents\\GitHub\\imednet-python-sdk\\docs\\todo\\04_data_models_and_serialization.md -->

**Objective:** Define Pydantic models for API data structures and handle serialization/deserialization.

**Key Requirements & Sub-Tasks:**

* [ ] **Define Pydantic models for all API structures.**
  * [ ] **Identify Task:** Create models in `imednet_sdk/models/` for responses and request bodies.
  * [ ] **Write/Update Tests:** Create `tests/test_models.py`. For each model, add tests to:
    * [ ] Verify successful deserialization from valid JSON (using examples from `docs/reference/` or fixtures).
    * [ ] Verify successful serialization to JSON.
    * [ ] Verify validation errors for incorrect data types or missing required fields.
    * [ ] Verify handling of optional fields and `null` values.
    * [ ] Verify custom validators (e.g., for dates) work correctly.
  * [ ] **Implement Code:**
    * [ ] Create `imednet_sdk/models/__init__.py`.
    * [ ] Create individual model files (e.g., `_common.py`, `study.py`, `site.py`, etc.) or group logically.
    * [ ] Define base models (`MetadataModel`, `ErrorDetailModel`, `FieldErrorModel`, `SortInfoModel`, `PaginationInfoModel`, `ApiResponseModel`, `JobStatusModel`) potentially in `_common.py`. Use `pydantic.BaseModel` and generics (`typing.TypeVar`, `typing.Generic`) where appropriate (e.g., `ApiResponseModel[T]`).
    * [ ] Define resource-specific models (`StudyModel`, `SiteModel`, etc.) inheriting from `BaseModel` or other relevant models. Refer heavily to `docs/reference/*.md`.
    * [ ] Implement custom date parsing/validation using Pydantic validators (`@validator`) or `Config` settings to handle various formats (`YYYY-MM-DDTHH:MM:SSZ`, `YYYY-MM-DD HH:MM:SS`, `YYYY-MM-DD`) and convert to `datetime.datetime` or `datetime.date`.
    * [ ] Use `typing.Optional`, `typing.List`, `typing.Dict`, `typing.Literal` as needed.
    * [ ] Handle dynamic fields like `recordData` in `RecordModel` (potentially using `Dict[str, Any]` or a more specific approach if possible).
    * [ ] Define request body models (e.g., `RecordCreateModel`).
  * [ ] **Run Specific Tests:** `pytest tests/test_models.py` (or more specific `-k model_name`).
  * [ ] **Debug & Iterate:** Fix model definitions or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document model structure, design choices, and validation logic in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues (linting, typing).
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_models.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(models): define pydantic models for API structures\"` (or break down into smaller commits per model group).

* [ ] **Integrate deserialization into the client.**
  * [ ] **Identify Task:** Modify the client's request methods to automatically deserialize successful JSON responses into Pydantic models.
  * [ ] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) to:
    * [ ] Verify that successful GET/POST requests return the appropriate Pydantic model instance (or list of instances) instead of raw JSON/dict.
    * [ ] Verify that validation errors during deserialization are handled correctly (e.g., raise a specific `DeserializationError` - see Task 06).
  * [ ] **Implement Code:**
    * [ ] Modify the `_request` method (or `get`/`post`) in `imednet_sdk/client.py`.
    * [ ] After receiving a successful response (`response.status_code` is 2xx), parse the JSON (`response.json()`).
    * [ ] Use the appropriate Pydantic model (potentially passed as an argument or determined based on the endpoint) to parse the JSON data (e.g., `ModelName.parse_obj(data)` or `parse_obj_as(List[ModelName], data)`).
    * [ ] Handle potential `pydantic.ValidationError` and wrap it in a custom exception (Task 06).
    * [ ] Return the parsed Pydantic model instance(s).
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [ ] **Debug & Iterate:** Fix client code or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document client deserialization logic in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): integrate pydantic deserialization into requests\"`

* [ ] **Integrate serialization into the client.**
  * [ ] **Identify Task:** Modify client methods (e.g., POST) to accept Pydantic models as input and serialize them to JSON for the request body.
  * [ ] **Write/Update Tests:** Update `tests/test_client.py` or specific API endpoint tests (Task 05) for POST requests to:
    * [ ] Verify that passing a Pydantic model instance as data works correctly.
    * [ ] Verify that the correct JSON payload is sent in the request body (using mocking).
  * [ ] **Implement Code:**
    * [ ] Modify methods like `post` in `imednet_sdk/client.py`.
    * [ ] Check if the `data` or `json` payload argument is a Pydantic `BaseModel` instance.
    * [ ] If it is, serialize it to a dictionary suitable for `httpx` (e.g., `model.dict(by_alias=True)` - consider excluding unset fields if appropriate).
    * [ ] Pass the resulting dictionary as the `json` parameter to `httpx.request`.
  * [ ] **Run Specific Tests:** `pytest tests/test_client.py` (or relevant endpoint tests).
  * [ ] **Debug & Iterate:** Fix client code or tests until specific tests pass.
  * [ ] **Run All Module Unit Tests:** `pytest tests/`
  * [ ] **Update Memory File:** Document client serialization logic in `docs/memory/04_data_models_and_serialization.md`.
  * [ ] **Stage Changes:** `git add .`
  * [ ] **Run Pre-commit Checks:** `pre-commit run --all-files`
  * [ ] **Fix Pre-commit Issues:** Address any reported issues.
  * [ ] **Re-run Specific Tests (Post-Fix):** `pytest tests/test_client.py`
  * [ ] **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
  * [ ] **Update Memory File (Post-Fix):** Note any significant fixes.
  * [ ] **Stage Changes (Again):** `git add .`
  * [ ] **Update Task List:** Mark this sub-task as done.
  * [ ] **Commit Changes:** `git commit -m \"feat(client): integrate pydantic serialization for request bodies\"`

**Acceptance Criteria:**

* [ ] Pydantic models exist for all documented API resources, requests, and common structures.
* [ ] Models correctly handle data types, nesting, optionality, and date formats.
* [ ] Unit tests exist for model validation, serialization, and deserialization.
* [ ] Client methods automatically deserialize successful JSON responses into the correct Pydantic models.
* [ ] Client methods accept Pydantic models as input for request bodies (where applicable) and serialize them correctly.
* [ ] Deserialization errors are handled appropriately (raising a custom exception).

**Notes:**

* This is a large task; consider breaking down model creation and testing per resource.
* The `scripts/generate_models.py` might be helpful but likely requires significant refinement or manual implementation.
* Pay close attention to the exact field names and structures in `docs/reference/`.
