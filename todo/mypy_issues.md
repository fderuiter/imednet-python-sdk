# **📝 mypy TODO List**

**Total Errors:** 30
**Files Affected:** 19

---

## imednet_sdk/exceptions.py (4)

- [ ] Line 122: `"SdkValidationError" has no attribute "attribute"`
- [ ] Line 123: `"SdkValidationError" has no attribute "attribute"`
- [ ] Line 124: `"SdkValidationError" has no attribute "value"`
- [ ] Line 125: `"SdkValidationError" has no attribute "value"`

## imednet_sdk/models/interval.py (1)

- [ ] Line 96: `"classmethod" used with a non-method`

## imednet_sdk/utils.py (2)

- [ ] Line 48: Dict entry 9 has incompatible type `tuple[object, dict[str, Any]]`; expected `tuple[type[Any], dict[str, Any]]`
- [ ] Line 188: Item “None” of `list[RecordModel] | None` has no attribute `__iter__`

## imednet_sdk/api/visits.py (1)

- [ ] Line 47: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[VisitModel]]`)

## imednet_sdk/api/variables.py (1)

- [ ] Line 51: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[VariableModel]]`)

## imednet_sdk/api/users.py (1)

- [ ] Line 54: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[UserModel]]`)

## imednet_sdk/api/subjects.py (1)

- [ ] Line 72: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[SubjectModel]]`)

## imednet_sdk/api/studies.py (2)

- [ ] Line 63: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[StudyModel]]`)
- [ ] Line 87: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[dict[Any, Any]]]`)

## imednet_sdk/api/sites.py (1)

- [ ] Line 72: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[SiteModel]]`)

## imednet_sdk/api/records.py (2)

- [ ] Line 93: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[RecordModel]]`)
- [ ] Line 150: Incompatible return type (got `list[Never] | Any`, expected `JobStatusModel`)

## imednet_sdk/api/record_revisions.py (1)

- [ ] Line 74: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[RecordRevisionModel]]`)

## imednet_sdk/api/queries.py (1)

- [ ] Line 68: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[QueryModel]]`)

## imednet_sdk/api/jobs.py (1)

- [ ] Line 46: Incompatible return type (got `list[Never] | Any`, expected `JobStatusModel`)

## imednet_sdk/api/intervals.py (1)

- [ ] Line 74: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[IntervalModel]]`)

## imednet_sdk/api/forms.py (1)

- [ ] Line 74: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[FormModel]]`)

## imednet_sdk/api/codings.py (1)

- [ ] Line 47: Incompatible return type (got `list[Never] | Any`, expected `ApiResponse[list[CodingModel]]`)

## imednet_sdk/client.py (6)

- [ ] Line 358: Item “None” of `Any | None` has no attribute `JSONDecodeError`
- [ ] Line 595: Too many arguments for `build_model_from_variables`
- [ ] Line 595: Argument 1 to `build_model_from_variables` has incompatible type `ImednetClient`; expected `list[dict[str, Any]]`
- [ ] Line 619: Incompatible return value type (got `list[Any]`, expected `ApiResponse[list[Any]]`)
- [ ] Line 619: Argument 1 to `_fetch_and_parse_typed_records` has incompatible type `ImednetClient`; expected `VariablesClient`
- [ ] Line 619: Argument 2 to `_fetch_and_parse_typed_records` has incompatible type `str`; expected `RecordsClient`

## tests/client/test_exceptions.py (1)

- [ ] Line 11: Module `imednet_sdk.exceptions` has no attribute `ValidationError`; maybe `SdkValidationError`?

## examples/handle_api_errors.py (1)

- [ ] Line 41: Module `imednet_sdk.exceptions` has no attribute `ValidationError`; maybe `SdkValidationError`?

---
