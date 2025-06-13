# Test Plan for 90% Coverage - imednet-python-sdk

**Current Coverage:** (Estimate based on single smoke test - likely < 5%)
**Target Coverage:** 90%

## Overview

The current test suite only includes a basic smoke test (`tests/unit/test_smoke.py`) which checks if the main SDK class can be imported. To reach 90% coverage, we need to add unit and integration tests for core functionality, endpoints, models, utilities, and workflows.

## Areas Requiring Tests

**1. Core Components (`imednet/core`)**

* **`client.py` (Class: `Client`):**
  * Test successful initialization with API keys/base URL.
  * Test handling of missing/invalid credentials.
  * Mock `httpx.AsyncClient` and test `_request` method:
    * Successful GET, POST, PUT, DELETE requests.
    * Correct header construction (API keys, Content-Type).
    * Correct URL building (base URL + path).
    * Handling of different HTTP status codes (2xx, 4xx, 5xx).
    * Parsing of successful JSON responses.
    * Raising `ApiError` on 4xx/5xx errors with correct details.
    * Retry logic (`tenacity` integration).
  * Test `get`, `post`, `put`, `delete` convenience methods.
  * Test `close` method.
* **`context.py` (Class: `Context`):**
  * Test initialization.
  * Test `set_default_study_key` and `clear_default_study_key`.
  * Test property access (`default_study_key`).
* **`exceptions.py` (Classes: `ImednetError`, `ApiError`):**
  * Test initialization of `ImednetError` and `ApiError`.
  * Test string representation (`__str__`) of errors, including status code and details for `ApiError`.
* **`paginator.py` (Class: `Paginator`):**
  * Mock `Client.get`.
  * Test asynchronous iteration (`__aiter__`, `__anext__`) over multiple pages.
  * Test handling of empty responses.
  * Test handling of responses with fewer items than `page_size`.
  * Test correct parameter construction (`page`, `size`, custom params).
  * Test handling of different `data_key` and `metadata_key`.
  * Test error handling if the underlying client call fails.

**2. Endpoints (`imednet/endpoints`)**

* **`base.py` (Class: `BaseEndpoint`):**
  * Test `_build_path` logic with various inputs.
  * Test `_list_paginated` method, mocking the `Paginator`.
* **Specific Endpoint Files:** (`codings.py`, `forms.py`, `intervals.py`, `jobs.py`, `queries.py`, `records.py`, `record_revisions.py`, `sites.py`, `studies.py`, `subjects.py`, `users.py`, `variables.py`, `visits.py`)
  * For *each* endpoint class (e.g., `StudiesEndpoint`, `RecordsEndpoint`, `SubjectsEndpoint`):
    * Mock the `Client` passed during initialization.
    * For *each* public method (e.g., `list`, `get`, `create`, `update`, `delete`):
      * Test successful calls:
        * Verify the correct client method (`get`, `post`, etc.) is called.
        * Verify the correct path is constructed using `_build_path`.
        * Verify correct parameters/payload are sent (including filters where applicable).
        * Verify the response JSON is correctly parsed into the expected Pydantic model(s) (e.g., `List[Study]`, `Record`, `Job`).
      * Test filter building (e.g., usage of `build_filter_string` if applicable internally, or correct passing of filter strings).
      * Test pagination usage (where applicable, e.g., `list` methods using `_list_paginated`).
      * Test handling of API errors raised by the client.

**3. Models (`imednet/models`)**

* **Specific Model Files:** (`base.py`, `codings.py`, `forms.py`, `intervals.py`, `jobs.py`, `queries.py`, `records.py`, `record_revisions.py`, `sites.py`, `studies.py`, `study_structure.py`, `subjects.py`, `users.py`, `validators.py`, `variables.py`, `visits.py`)
  * For *each* Pydantic model (e.g., `Study`, `Record`, `Keyword`, `QueryComment`, `Site`, `Subject`, `User`, `Variable`, `Visit`, `Form`, `Interval`, `Job`, `Coding`, `RecordRevision`, `StudyStructure`):
    * Test successful instantiation from a dictionary (simulating API JSON). Use `model_validate`.
    * Test handling of missing optional fields (should default correctly).
    * Test handling of fields with aliases (`populate_by_name=True` behavior via `model_validate`).
    * Test custom validators (`@field_validator` in `validators.py` or within models):
      * Valid input data (dates, ints, bools, strings).
      * Invalid/malformed input data (should raise `ValidationError`).
      * Edge cases (e.g., empty strings, `None` values passed to validators).
    * Test `model_dump(by_alias=True)` produces the expected dictionary structure for API calls.

**4. Utilities (`imednet/utils`)**

* **`dates.py`:**
  * Test `parse_iso_datetime` with valid, invalid, and timezone-aware/naive ISO strings. Test `None` input.
  * Test `format_iso_datetime` with `datetime` objects and `None`.
* **`filters.py` (Function: `build_filter_string`):**
  * Test with various dictionary inputs:
    * Simple key-value pairs (string, int, bool).
    * Multiple key-value pairs.
    * Keys requiring special handling (if any defined).
    * Empty dictionary.
    * Dictionary with `None` values (should be skipped).
    * Dictionary with boolean values (should convert to 'true'/'false').
* **`typing.py`:** (No runtime logic to test, only type definitions).

**5. Workflows (`imednet/workflows`)**

* **Specific Workflow Files:** (`data_extraction.py`, `query_management.py`, `record_mapper.py`, `record_update.py`, `register_subjects.py`, `study_structure.py`, `subject_data.py`)
  * Mock the `ImednetSDK` instance and its endpoint methods (`sdk.studies.list`, `sdk.records.list`, etc.).
  * For *each* workflow class/function (e.g., `DataExtractionWorkflow`, `QueryManagementWorkflow`, `RecordMapper`, `RecordUpdateWorkflow`, `SubjectDataWorkflow`, `fetch_study_structure`):
    * Test the main execution path with mocked successful API responses from endpoints.
    * Verify the correct sequence of SDK endpoint calls.
    * Verify correct parameters are passed to SDK methods (study keys, filters).
    * Verify data aggregation/transformation logic (e.g., combining results, mapping data).
    * Test handling of empty or partial results from API calls.
    * Test error handling if underlying SDK calls fail (propagate `ApiError`).
  * **`record_mapper.py` (Class: `RecordMapper`) Specific:**
    * Test `map_records_to_dataframe` logic.
    * Test DataFrame creation, column naming (labels vs. names), and structure.
    * Test handling of missing variables/columns.
    * Test type conversion/validation within the DataFrame.
    * Test filtering logic (e.g., `visit_key`, `form_key`).
  * **`study_structure.py` (Function: `fetch_study_structure`) Specific:**
    * Test aggregation of intervals, forms, and variables into the nested `StudyStructure` model by mocking `sdk.intervals.list`, `sdk.forms.list`, `sdk.variables.list`.

**6. SDK Entrypoint (`imednet/sdk.py`)**

* **Class: `ImednetSDK`:**
  * Test initialization:
    * Correct instantiation of `Client`.
    * Correct instantiation and attachment of all endpoint classes (e.g., `sdk.studies`, `sdk.records`).
    * Correct instantiation and attachment of the `Workflows` namespace and its classes (e.g., `sdk.workflows.data_extraction`).
    * Passing credentials, base URL, timeout, retries correctly to `Client`.
  * Test context management (`__enter__`, `__exit__` calling `close`).
  * Test `close` method calls `client.close`.
  * Test `set_default_study` and `clear_default_study` correctly interact with `Context`.

**7. CLI (`imednet/cli.py`)**

* Use `typer.testing.CliRunner`.
* Mock `get_sdk()` to return a mocked `ImednetSDK` instance. Mock the relevant methods on the mocked SDK (e.g., `sdk.studies.list`, `sdk.subjects.list`, `workflow.extract_records_by_criteria`).
* For *each* command (e.g., `studies list`, `sites list`, `subjects list`, `workflows extract-records`):
  * Test successful execution with required arguments/options.
  * Verify correct mocked SDK methods are called with parsed arguments/filters.
  * Test output formatting (assert expected strings in `result.stdout`, potentially mock `rich.print`).
  * Test handling of missing arguments/options (check for `UsageError` in `result.exit_code`).
  * Test error handling (mock SDK methods to raise `ApiError`, check `result.exit_code` and error message in `result.stdout`).
  * Test filter argument parsing (`parse_filter_args` indirectly via command options).
  * Test environment variable handling for authentication (mock `os.getenv`).

## Implementation Strategy

1. **Prioritize Core & Models:** Start with `imednet/core` (`client.py`, `exceptions.py`, `paginator.py`) and `imednet/models` (all model files, `validators.py`). Ensure robust model validation and client request/error handling.
2. **Utilities:** Cover utility functions (`dates.py`, `filters.py`).
3. **Endpoints:** Test each endpoint file (`studies.py`, `records.py`, etc.) methodically, mocking client responses.
4. **Workflows:** Test workflow files (`data_extraction.py`, etc.) by mocking the SDK methods they rely on.
5. **SDK & CLI:** Test the main `sdk.py` class and the `cli.py` commands last, mocking lower-level components.
6. **Use `pytest` fixtures:** Create fixtures for initializing mocked SDKs, clients, sample API response data (dictionaries), and Pydantic models.
7. **Use `pytest-asyncio`:** For testing `async` functions (client, paginator, async endpoints/workflows).
8. **Use `responses` or `respx` library:** Useful for mocking HTTP requests/responses at the `httpx` level for client tests.
9. **Use `typer.testing.CliRunner`:** For testing CLI commands.

By systematically adding tests for these specific files and classes/functions, focusing on both successful paths and error conditions, the project should be able to achieve the 90% coverage target.

## Live End-to-End Tests

Real API integration tests are optional but recommended. See `LIVE_TEST_PLAN.md` in
this directory for a complete list of features. Every endpoint, workflow method, CLI
command (including export and job utilities), and integration helper should have a
dedicated live test that runs only when `IMEDNET_RUN_E2E=1` and valid credentials are
supplied.
