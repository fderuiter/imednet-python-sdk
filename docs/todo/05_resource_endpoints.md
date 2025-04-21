# Task 05: Resource Endpoint Implementations

**Objective:** Implement client classes and methods for each API resource endpoint.

**Definition of Done:**

* Separate client classes exist for each resource type in `imednet_sdk/api/`.
* Methods corresponding to each documented API endpoint are implemented.
* Methods correctly handle path parameters, query parameters (pagination, sorting, filtering), and request bodies.
* Methods accept and return the appropriate Pydantic models (Task 4).
* Methods raise specific exceptions on API errors (Task 6).
* Unit tests exist for each method, covering success and error cases, parameter handling, and model parsing.
* Resource clients are accessible via the main `ImednetClient` instance.

**Workflow Steps (Apply per Resource/Method):**

1. **Identify Task:** Select a resource (e.g., Studies) and a method (e.g., `list_studies`) from the Sub-Tasks list below.
2. **Write/Update Tests (TDD):**
   * Navigate to `tests/api/`.
   * Create/update the test file (e.g., `test_studies.py`).
   * Mock the HTTP request using `requests-mock` or `respx`.
   * Define expected URL, method, headers, query parameters (pagination, sorting, filtering), and request body (for POST).
   * Define mock success response (2xx status, JSON body with `metadata` and `data` matching Pydantic models from Task 4).
   * Define mock error responses (4xx/5xx status, JSON body matching error structure from Task 6).
   * Write tests asserting:
     * Correct request parameters are sent.
     * Successful response is deserialized into the correct Pydantic model (`ApiResponseModel[ResourceType]`).
     * Correct custom exceptions (Task 6) are raised for error responses.
     * Pagination/filtering/sorting parameters are handled correctly.
3. **Implement Code:**
   * Navigate to `imednet_sdk/api/`.
   * Create/update the resource client class (e.g., `studies.py`).
   * Define the method (e.g., `list_studies`).
   * Call the base client's request method (`_request`, `get`, `post`).
   * Pass correct path parameters, query parameters (handling defaults, pagination, sorting, filtering), and data (serializing Pydantic models for POST).
   * Specify the expected response Pydantic model for deserialization.
4. **Run Specific Tests:** `pytest tests/api/test_<resource>.py -k <method_name>` (e.g., `pytest tests/api/test_studies.py -k list_studies`)
5. **Debug & Iterate:** Fix implementation or tests until specific tests pass.
6. **Run All Module Unit Tests:** `pytest tests/api/`
7. **Update Memory File:** Document implementation details in `docs/memory/05_resource_endpoints.md` (or resource-specific memory files).
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Tests (Post-Fix):** `pytest tests/api/test_<resource>.py -k <method_name>`
12. **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/api/`
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the specific method/resource sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/05_resource_endpoints.md`
16. **Commit Changes:** `git commit -m "feat(api): implement <resource> client <method_name> method"` (Adjust scope and message).

**Sub-Tasks:**

* [x] **Base Resource Client:**
  * [x] Define a base class (e.g., `ResourceClient`) in `imednet_sdk/api/_base.py` that resource clients can inherit from. It should store a reference to the main `ImednetClient` instance.
* [x] **StudiesClient (`imednet_sdk/api/studies.py`)**
  * [x] `list_studies(**kwargs)`: `GET /api/v1/edc/studies`
    * Params: `page`, `size`, `sort`, `filter`
    * Headers: `x-api-key`, `x-imn-security-key`
* [ ] **SitesClient (`imednet_sdk/api/sites.py`)**
  * [ ] `list_sites(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/sites`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **FormsClient (`imednet_sdk/api/forms.py`)**
  * [ ] `list_forms(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/forms`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **IntervalsClient (`imednet_sdk/api/intervals.py`)**
  * [ ] `list_intervals(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/intervals`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **RecordsClient (`imednet_sdk/api/records.py`)**
  * [ ] `list_records(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/records`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`, `recordDataFilter`
  * [ ] `create_records(study_key: str, records: List[RecordCreateModel], email_notify: Optional[str] = None, **kwargs)`: `POST /api/v1/edc/studies/{studyKey}/records`
    * Path Params: `studyKey`
    * Headers: Optional `x-email-notify`
    * Body: Array of record objects. Returns job status (`jobId`, `batchId`, `state`).
* [ ] **RecordRevisionsClient (`imednet_sdk/api/record_revisions.py`)**
  * [ ] `list_record_revisions(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/recordRevisions`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **VariablesClient (`imednet_sdk/api/variables.py`)**
  * [ ] `list_variables(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/variables`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **CodingsClient (`imednet_sdk/api/codings.py`)**
  * [ ] `list_codings(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/codings`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **SubjectsClient (`imednet_sdk/api/subjects.py`)**
  * [ ] `list_subjects(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/subjects`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **UsersClient (`imednet_sdk/api/users.py`)**
  * [ ] `list_users(study_key: str, include_inactive: bool = False, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/users`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `includeInactive`
* [ ] **VisitsClient (`imednet_sdk/api/visits.py`)**
  * [ ] `list_visits(study_key: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/visits`
    * Path Params: `studyKey`
    * Params: `page`, `size`, `sort`, `filter`
* [ ] **JobsClient (`imednet_sdk/api/jobs.py`)**
  * [ ] `get_job_status(study_key: str, batch_id: str, **kwargs)`: `GET /api/v1/edc/studies/{studyKey}/jobs/{batchId}`
    * Path Params: `studyKey`, `batchId`
* [ ] **Integrate Resource Clients into Main Client:**
  * [ ] Add properties to `ImednetClient` (e.g., `client.studies`, `client.sites`) that initialize and return instances of the resource clients, passing the main client instance to them.
