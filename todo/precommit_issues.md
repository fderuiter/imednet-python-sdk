# TODO: Pre-commit Issues (as of 2025-04-22)

This file tracks the remaining issues identified by `pre-commit run --all-files`.

## Flake8 Issues

- [ ] **E501 (Line too long > 100 chars):**
  - [ ] `examples/create_new_record.py` (lines 95, 125)
  - [ ] `examples/find_subjects_by_status.py` (line 80)
  - [ ] `examples/get_all_records_for_subject.py` (lines 77, 91)
  - [ ] `examples/handle_api_errors.py` (lines 107, 167, 171)
  - [ ] `examples/list_studies_and_sites.py` (line 128)
  - [ ] `examples/usage_example.py` (line 103)
  - [ ] `imednet_sdk/client.py` (lines 23, 261)
  - [ ] `imednet_sdk/models/interval.py` (lines 72, 74)
  - [ ] `imednet_sdk/models/record.py` (line 45)
  - [ ] `imednet_sdk/models/subject.py` (line 3)
  - [ ] `tests/api/test_jobs.py` (lines 74, 98)
  - [ ] `tests/client/test_retries.py` (line 106)
  - [ ] `tests/models/test_job_model.py` (line 23)
  - [ ] `tests/test_client.py` (lines 15, 415)
- [ ] **E402 (Module level import not at top of file):**
  - [ ] `examples/get_all_records_for_subject.py` (lines 38, 39, 40, 42, 44, 45, 46)
- [ ] **F401 (Unused import):**
  - [ ] `imednet_sdk/api/studies.py` (typing Any, Dict, List, Optional; ..exceptions.ImednetSdkException)
  - [ ] `imednet_sdk/client.py` (`imednet_sdk.models._common.ApiResponse`)
  - [ ] `imednet_sdk/models/record.py` (`..exceptions.ImednetSdkException`)
  - [ ] `imednet_sdk/utils.py` (`.models.RecordModel`, `.models.VariableModel`)
  - [ ] `tests/api/test_jobs.py` (`datetime`)
  - [ ] `tests/client/conftest.py` (`unittest.mock.MagicMock`)
  - [ ] `tests/client/test_request_handling.py` (`unittest.mock.MagicMock`, `unittest.mock.patch`, `imednet_sdk.client.ImednetClient`)
  - [ ] `tests/client/test_retries.py` (`tenacity.RetryError`)
- [ ] **F811 (Redefinition of unused variable):**
  - [ ] `imednet_sdk/api/studies.py` (`ApiResponse`, `StudyModel` from line 9/10 redefined on line 13)
  - [ ] `imednet_sdk/utils.py` (`RecordModel`, `VariableModel` from line 23 redefined on line 140)
- [ ] **F841 (Local variable assigned but never used):**
  - [ ] `tests/api/test_codings.py` (line 105: `params`)
  - [ ] `tests/api/test_forms.py` (line 144: `params`)
  - [ ] `tests/api/test_intervals.py` (line 137: `params`)
  - [ ] `tests/api/test_studies.py` (lines 302, 323: `expected_url_pattern`)
  - [ ] `tests/models/test_common_models.py` (line 73: `pagination_data`)
  - [ ] `tests/models/test_job_model.py` (line 150: `model`)

## MyPy Issues

- [ ] **`no-redef` (Name already defined):**
  - [ ] `imednet_sdk/models/record.py`: `recordId` (line 92 from 72), `subjectId` (line 95 from 76), `subjectKey` (line 98 from 78), `siteId` (line 101 from 71), `formId` (line 107 from 69), `formKey` (line 110 from 70), `intervalId` (line 117 from 68), `recordStatus` (line 128 from 75), `dateCreated` (line 137 from 82)
  - [ ] `imednet_sdk/models/interval.py`: `intervalId` (line 126 from 84), `intervalName` (line 129 from 85)
- [ ] **`dict-item` (Incompatible type in dict):**
  - [ ] `imednet_sdk/utils.py`: Multiple entries in `TYPE_MAP` (lines 31, 38–45, 48)
- [ ] **`attr-defined` (Attribute not found):**
  - [ ] `imednet_sdk/utils.py`: `ResourceClient` has no attribute `list_variables` (line 144), `list_records` (line 182)
- [ ] **`return-value` (Incompatible return value type):**
  - [ ] `imednet_sdk/api/visits.py` (line 47)
  - [ ] `imednet_sdk/api/variables.py` (line 51)
  - [ ] `imednet_sdk/api/users.py` (line 54)
  - [ ] `imednet_sdk/api/subjects.py` (line 74)
  - [ ] `imednet_sdk/api/studies.py` (lines 38, 57, 76, 99)
  - [ ] `imednet_sdk/api/sites.py` (line 74)
  - [ ] `imednet_sdk/api/records.py` (lines 83, 140)
  - [ ] `imednet_sdk/api/record_revisions.py` (line 74)
  - [ ] `imednet_sdk/api/queries.py` (line 68)
  - [ ] `imednet_sdk/api/jobs.py` (line 46)
  - [ ] `imednet_sdk/api/intervals.py` (line 74)
  - [ ] `imednet_sdk/api/forms.py` (line 74)
  - [ ] `imednet_sdk/api/codings.py` (line 47)
- [ ] **`arg-type` (Argument type mismatch):**
  - [ ] `imednet_sdk/api/studies.py`: `_get` call with `response_model` of wrong type (line 101)
- [ ] **`func-returns-value` (Missing return value):**
  - [ ] `imednet_sdk/client.py`: `_handle_api_error` does not return a value but is annotated to do so (line 225)
- [ ] **`annotation-unchecked` (Consider `--check-untyped-defs`):**
  - [ ] `examples/get_all_records_for_subject.py` (line 80)
