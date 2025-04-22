# TODO: Pre-commit Issues (as of 2025-04-21)

This file tracks the remaining issues identified by `pre-commit run --all-files`.

## Flake8 Issues

* **E501 (Line too long > 100 chars):**
  * `examples/create_new_record.py` (lines 95, 125)
  * `examples/find_subjects_by_status.py` (line 80)
  * `examples/get_all_records_for_subject.py` (lines 77, 91)
  * `examples/handle_api_errors.py` (lines 107, 167, 171)
  * `examples/list_studies_and_sites.py` (line 128)
  * `examples/usage_example.py` (line 103)
  * `imednet_sdk/client.py` (lines 23, 515)
  * `imednet_sdk/models/interval.py` (lines 72, 74)
  * `imednet_sdk/models/record.py` (line 42)
  * `imednet_sdk/models/subject.py` (line 3)
  * `tests/client/test_retries.py` (line 106)
  * `tests/models/test_job_model.py` (line 23)
  * `tests/test_client.py` (lines 15, 415)
* **E402 (Module level import not at top of file):**
  * `examples/get_all_records_for_subject.py` (lines 38, 39, 40, 42, 44, 45, 46)
* **F401 (Unused import):**
  * `imednet_sdk/api/studies.py` (typing Any, Dict, List, Optional; ImednetSdkException)
  * `imednet_sdk/client.py` (`_fetch_and_parse_typed_records`)
  * `tests/api/test_jobs.py` (`datetime.datetime`)
  * `tests/client/conftest.py` (`unittest.mock.MagicMock`)
  * `tests/client/test_request_handling.py` (`unittest.mock.MagicMock`, `unittest.mock.patch`, `imednet_sdk.client.ImednetClient`)
  * `tests/client/test_retries.py` (`tenacity.RetryError`)
* **F811 (Redefinition of unused variable):**
  * `imednet_sdk/api/studies.py` (`ApiResponse`, `StudyModel` from line 9/10 redefined on line 13)
* **F821 (Undefined name):**
  * `imednet_sdk/client.py` (line 532: `get_typed_records_for_subject`)
* **F841 (Local variable assigned but never used):**
  * `tests/api/test_codings.py` (line 105: `params`)
  * `tests/api/test_forms.py` (line 144: `params`)
  * `tests/api/test_intervals.py` (line 137: `params`)
  * `tests/api/test_jobs.py` (line 37: `expected_url`)
  * `tests/api/test_studies.py` (lines 302, 323: `expected_url_pattern`)
  * `tests/models/test_common_models.py` (line 73: `pagination_data`)
  * `tests/models/test_job_model.py` (line 150: `model`)

## MyPy Issues

* **`no-redef` (Name already defined):**
  * `imednet_sdk/models/interval.py`: `intervalId` (line 126 from 84), `intervalName` (line 129 from 85)
  * `imednet_sdk/models/record.py`: `recordId` (line 89 from 69), `subjectId` (line 92 from 73), `subjectKey` (line 95 from 75), `siteId` (line 98 from 68), `formId` (line 104 from 66), `formKey` (line 107 from 67), `intervalId` (line 114 from 65), `recordStatus` (line 125 from 72), `dateCreated` (line 134 from 79)
* **`dict-item` (Incompatible type in dict):**
  * `imednet_sdk/utils.py`: Multiple entries in `TYPE_MAP` (lines 31, 38-45, 48)
* **`attr-defined` (Attribute not found):**
  * `imednet_sdk/utils.py`: `ResourceClient` has no attribute `list_variables` (line 141), `list_records` (line 179)
  * `imednet_sdk/models/record.py`: Module `imednet_sdk.utils` has no attribute `parse_datetime_string_optional` (line 13)
  * `imednet_sdk/api/studies.py`: `StudiesClient` has no attribute `_request` (lines 37, 57, 80, 104)
* **`call-arg` (Unexpected keyword argument):**
  * `imednet_sdk/api/_base.py`: Unexpected `timeout` for `_request` (lines 74, 107)
  * `imednet_sdk/client.py`: Unexpected `timeout` for `_request` (lines 476, 507)
* **`return-value` (Incompatible return value type):**
  * `imednet_sdk/api/visits.py` (line 46)
  * `imednet_sdk/api/variables.py` (line 50)
  * `imednet_sdk/api/users.py` (line 56)
  * `imednet_sdk/api/subjects.py` (line 73)
  * `imednet_sdk/api/sites.py` (line 75)
  * `imednet_sdk/api/records.py` (lines 82, 141)
  * `imednet_sdk/api/record_revisions.py` (line 73)
  * `imednet_sdk/api/queries.py` (line 68)
  * `imednet_sdk/api/jobs.py` (line 45)
  * `imednet_sdk/api/intervals.py` (line 73)
  * `imednet_sdk/api/forms.py` (line 73)
  * `imednet_sdk/api/codings.py` (line 46)
* **`name-defined` (Name not defined):**
  * `imednet_sdk/client.py`: `get_typed_records_for_subject` (line 532)
* **`annotation-unchecked` (Consider `--check-untyped-defs`):**
  * `examples/get_all_records_for_subject.py` (line 80)
