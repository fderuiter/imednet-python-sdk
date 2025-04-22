# 2025-04-22 Pytest Issues (Updated)

## **Errors (Priority)**

- [ ] **Implement `get_typed_records` in `ImednetClient`** (`AttributeError`)
  - Add a `get_typed_records(study_key, form_key, **kwargs)` method (Tests failing: `test_get_typed_records_*` in `test_client.py` and `test_get_typed_records.py`)
  - Call `self.variables.list_variables(studyKey=study_key)` and propagate any `ApiError`
  - Build the Pydantic model via `build_model_from_variables(...)`, letting exceptions bubble up
  - Call `self.records.list_records(studyKey=study_key, formKey=form_key, **kwargs)`
    - Combine any existing `filter` kwarg with `formKey==<form_key>`
    - Support `size`, `sort`, `record_data_filter`, etc.
  - Return the parsed, typed record list

- [ ] **Fix `respx` mocks for `/studies` endpoint** (`AllMockedAssertionError`)
  - Ensure the exact URL paths and query-string formats (including encoding) used in `test_list_studies_*` tests match the client's actual calls. (Tests failing: `test_list_studies_*` in `test_studies.py`)

- [ ] **Improve JSON serialization & deserialization in HTTP methods**
  - In `_get`, catch `json.JSONDecodeError` and raise `RuntimeError("Failed to decode JSON response")` (Tests failing: `test_get_deserialization_invalid_json` in `test_serialization.py`, `test_client.py`)
  - Before sending in `_post`, detect any Pydantic `BaseModel` passed to the `json=` param and replace with `model_dump(by_alias=True)` (Tests failing: `test_post_serialization*` in `test_serialization.py`, `test_client.py`)
  - After receiving a response, if `response_model` is provided, call `response_model.model_validate(...)` on the JSON (Verify this part)

- [ ] **Make Pydantic models align with test expectations**
  - **`ApiResponse`**: mark `metadata` as required, even if `pagination` is `None`. (Test failing: `test_api_response_no_pagination` in `test_common_models.py`)
  - **`JobStatusModel`**:
    - Add `dateStarted` and `dateFinished` fields (optional, `datetime | None = None`). (Test failing: `test_get_job_status_success` in `test_jobs.py`)
    - Change `batchId` type to `str`. (Test failing: `test_job_status_model_serialization` in `test_job_model.py`)
    - Make `jobId` and `dateCreated` required (remove defaults). (Test failing: `test_job_status_model_serialization` in `test_job_model.py`)
  - **`IntervalModel`**: ensure `intervalName` is required so omitting it raises `ValidationError`. (Test failing: `test_interval_model_missing_required_field` in `test_interval_model.py`)
  - **`RecordModel`**: enforce required fields (e.g. `formKey`) so missing ones trigger `ValidationError`. (Test failing: `test_record_model_missing_required_field` in `test_record_model.py`)

## **Failures**

- [ ] **Adjust retry logic so 4xx errors are not retried** (`AssertionError`)
  - Configure your Tenacity retryer for `_get` and `_post` to **not** retry on:
    - `NotFoundError` (404) (Tests failing: `test_no_retry_on_4xx_error`, `test_tenacity_no_retry_on_notfound_error_get` in `test_retries.py`, `test_client.py`)
    - `RateLimitError` (429) (Test failing: `test_tenacity_no_retry_on_ratelimit_post` in `test_retries.py`, `test_client.py`)
    - `AuthenticationError` (401) (Test failing: `test_tenacity_no_retry_on_authentication_error_get` in `test_retries.py`, `test_client.py`)
    - Any other client-side HTTP error (Verify `BadRequestError` (400), `AuthorizationError` (403) are not retried)

- [ ] **Fix & flesh out API client methods in `imednet_sdk.api`**
  - **Jobs** (`test_get_job_status_running`): Adjust test assertion or model handling for date comparison (`AssertionError`).
  - **Studies** (`test_list_studies_*`): Implement `list_studies(page, size, sort, filter)` - *Covered by `respx` error above*.
    - Hit `/studies` with correct query params (string filters wrapped in quotes)
    - Return `ApiResponse[List[StudyModel]]`
    - Cover tests for pagination, sorting, filtering, empty results, and 400/401/403/404/500 error handling - *Partially covered by `respx` error above*.

- [ ] **Verify your `respx` mocks match the real request patterns** - *Covered by `respx` error above*.
  - Ensure the exact URL paths and query-string formats used in tests line up with your client’s calls
