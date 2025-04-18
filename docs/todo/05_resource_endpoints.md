# Task 5: Resource Endpoint Implementations

- Implement individual clients for each API resource:
  - **SitesClient**: GET `/api/v1/edc/studies/{studyKey}/sites`, supports `page`, `size`, `sort`, `filter` (see docs/reference/sites.md)
  - **StudiesClient**: GET `/api/v1/edc/studies`, POST `/api/v1/edc/studies`, GET/PUT/DELETE `/api/v1/edc/studies/{studyKey}` (see docs/reference/studies.md)
  - **SubjectsClient**: GET `/api/v1/edc/studies/{studyKey}/subjects`, supports pagination/filter (docs/reference/subjects.md)
  - **VisitsClient**: GET `/api/v1/edc/studies/{studyKey}/subjects/{subjectKey}/visits`, CRUD operations (docs/reference/visits.md)
  - **VariablesClient**: GET `/api/v1/edc/studies/{studyKey}/variables`, supports metadata and filter (docs/reference/variables.md)
  - **RecordsClient**: GET `/api/v1/edc/studies/{studyKey}/subjects/{subjectKey}/records`, POST to create records (docs/reference/records.md)
  - **RecordRevisionsClient**: GET `/api/v1/edc/records/{recordId}/revisions` (docs/reference/record_revisions.md)
  - **JobsClient**: POST `/api/v1/edc/jobs`, GET `/api/v1/edc/jobs/{jobId}` (docs/reference/jobs.md)
  - **UsersClient**: GET `/api/v1/edc/users`, GET `/api/v1/edc/users/{userId}` (docs/reference/users.md)
- Map each endpoint to client methods with typed request/response models
- Consistently handle path and query parameters per reference specifications
- Ensure header enforcement and error handling are applied to all methods
