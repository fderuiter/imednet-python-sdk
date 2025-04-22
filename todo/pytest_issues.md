# 2025-04-21 Pytest Issues

- [ ] **Implement `get_typed_records` in `ImednetClient`**  
  - Add a `get_typed_records(study_key, form_key, **kwargs)` method  
  - Call `self.variables.list_variables(studyKey=study_key)` and propagate any `ApiError`  
  - Build the Pydantic model via `build_model_from_variables(...)`, letting exceptions bubble up  
  - Call `self.records.list_records(studyKey=study_key, formKey=form_key, **kwargs)`  
    - Combine any existing `filter` kwarg with `formKey==<form_key>`  
    - Support `size`, `sort`, `record_data_filter`, etc.  
  - Return the parsed, typed record list

- [ ] **Adjust retry logic so 4xx errors are not retried**  
  - Configure your Tenacity retryer for `_get` and `_post` to **not** retry on:  
    - `NotFoundError` (404)  
    - `RateLimitError` (429)  
    - `AuthenticationError` (401)  
    - Any other client‑side HTTP error  

- [ ] **Improve JSON serialization & deserialization in HTTP methods**  
  - In `_get`, catch JSON decode failures and raise `RuntimeError("Failed to decode JSON response")`  
  - Before sending, detect any Pydantic `BaseModel` passed to the `json=` param and replace with `model_dump(by_alias=True)`  
  - After receiving a response, if `response_model` is provided, call `response_model.model_validate(...)` on the JSON

- [ ] **Make Pydantic models align with test expectations**  
  - **`ApiResponse`**: mark `pagination` as optional (default `None`) so “no pagination” payloads don’t error  
  - **`IntervalModel`**: ensure `intervalName` is required so omitting it raises `ValidationError`  
  - **`JobStatusModel`**:  
    - Change `batchId` type to `str`  
    - Make `jobId` and `dateCreated` optional with default `None`  
  - **`RecordModel`**: enforce required fields (e.g. `formKey`) so missing ones trigger `ValidationError`

- [ ] **Fix & flesh out API client methods in `imednet_sdk.api`**  
  - **Jobs** (`test_get_job_status_success`): add a `get_job_status(job_id)` that calls `/jobs/{job_id}/status` and returns a `JobStatusModel`  
  - **Studies** (`test_list_studies_*`): implement `list_studies(page, size, sort, filter)`  
    - Hit `/studies` with correct query params (string filters wrapped in quotes)  
    - Return `ApiResponse[List[StudyModel]]`  
    - Cover tests for pagination, sorting, filtering, empty results, and 400/401/403/404/500 error handling

- [ ] **Verify your `respx` mocks match the real request patterns**  
  - Ensure the exact URL paths and query‑string formats used in tests line up with your client’s calls  
