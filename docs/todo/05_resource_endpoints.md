<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\todo\05_resource_endpoints.md -->
# Task 5: Resource Endpoint Implementations

- [ ] Create separate client classes for each resource type in `imednet_sdk/api/`, inheriting from `BaseClient`.
- [ ] Implement methods corresponding to each documented API endpoint, using the Pydantic models defined in Task 4 for request bodies and response parsing.

- [ ] **StudiesClient (`imednet_sdk/api/studies.py`)**
  - `list_studies()`: `GET /api/v1/edc/studies` (Supports pagination, sorting by `studyKey`, filtering by `studyKey`, `studyName`, etc.) - Ref: `studies.md`
  - *Note: POST/PUT/DELETE for studies are not documented in the provided reference.*

- [ ] **SitesClient (`imednet_sdk/api/sites.py`)**
  - `list_sites(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/sites` (Supports pagination, sorting by `siteId`, filtering by `siteId`, `siteName`, etc.) - Ref: `sites.md`

- [ ] **FormsClient (`imednet_sdk/api/forms.py`)**
  - `list_forms(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/forms` (Supports pagination, sorting by `formId`, filtering by `formId`, `formKey`, `formType`, etc.) - Ref: `forms.md`

- [ ] **IntervalsClient (`imednet_sdk/api/intervals.py`)**
  - `list_intervals(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/intervals` (Supports pagination, sorting by `intervalId`, filtering by `intervalId`, `intervalName`, etc.) - Ref: `intervals.md`

- [ ] **RecordsClient (`imednet_sdk/api/records.py`)**
  - `list_records(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/records` (Supports pagination, sorting by `recordId`, filtering by standard fields, and `recordDataFilter`) - Ref: `records.md`
  - `create_records(study_key: str, records: List[RecordCreateModel], email_notify: Optional[str] = None)`: `POST /api/v1/edc/studies/{studyKey}/records` (Requires request body, optional `x-email-notify` header) - Ref: `records.md`

- [ ] **RecordRevisionsClient (`imednet_sdk/api/record_revisions.py`)**
  - `list_record_revisions(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/recordRevisions` (Supports pagination, sorting by `recordRevisionId`, filtering by `recordId`, `subjectKey`, `user`, etc.) - Ref: `record_revisions.md`

- [ ] **VariablesClient (`imednet_sdk/api/variables.py`)**
  - `list_variables(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/variables` (Supports pagination, sorting by `variableId`, filtering by `variableId`, `formId`, `formKey`, etc.) - Ref: `variables.md`

- [ ] **CodingsClient (`imednet_sdk/api/codings.py`)**
  - `list_codings(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/codings` (Supports pagination, sorting by `recordId`, filtering by `dictionaryName`, `codedBy`, etc.) - Ref: `codings.md`

- [ ] **SubjectsClient (`imednet_sdk/api/subjects.py`)**
  - `list_subjects(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/subjects` (Supports pagination, sorting by `subjectId`, filtering by `subjectId`, `subjectKey`, `siteName`, etc.) - Ref: `subjects.md`

- [ ] **UsersClient (`imednet_sdk/api/users.py`)**
  - `list_users(study_key: str, include_inactive: bool = False)`: `GET /api/v1/edc/studies/{studyKey}/users` (Supports pagination, sorting by `login`, `includeInactive` param) - Ref: `users.md`

- [ ] **VisitsClient (`imednet_sdk/api/visits.py`)**
  - `list_visits(study_key: str)`: `GET /api/v1/edc/studies/{studyKey}/visits` (Supports pagination, sorting by `visitId`, filtering by `subjectKey`, `intervalName`, `visitDate`, etc.) - Ref: `visits.md`

- [ ] **JobsClient (`imednet_sdk/api/jobs.py`)**
  - `get_job_status(study_key: str, batch_id: str)`: `GET /api/v1/edc/studies/{studyKey}/jobs/{batchId}` - Ref: `jobs.md`

- [ ] Ensure all client methods correctly handle path parameters (like `studyKey`, `batchId`).
- [ ] Ensure query parameters (`page`, `size`, `sort`, `filter`, `recordDataFilter`, `includeInactive`) are passed correctly.
- [ ] Ensure methods return the deserialized Pydantic models (e.g., `ApiResponseModel[StudyModel]`, `JobStatusModel`).
- [ ] Integrate error handling (Task 6) to raise specific exceptions on API errors.
