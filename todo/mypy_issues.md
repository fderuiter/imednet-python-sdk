# 📝 mypy TODO List

**Total Errors:** 42
**Files Affected:** 18

---

## ✅ imednet_sdk/models/interval.py

- [x] Line 96: Fix `"classmethod"` used with a non-method

## ✅ imednet_sdk/utils.py

- [x] Line 48: Fix incompatible dict entry type (use `type[Any]` instead of `tuple[type[Any], dict[str, Any]]`)
- [x] Line 141: Add `list_variables` attribute to `ResourceClient` or fix usage
- [x] Line 188: Add `list_records` attribute to `ResourceClient` or fix usage

## ✅ imednet_sdk/api/visits.py

- [x] Line 47: Fix return type to `ApiResponse[list[VisitModel]]`

## ✅ imednet_sdk/api/variables.py

- [x] Line 51: Fix return type to `ApiResponse[list[VariableModel]]`

## ✅ imednet_sdk/api/users.py

- [x] Line 54: Fix return type to `ApiResponse[list[UserModel]]`

## ✅ tests/client/test_get_typed_records.py

- [x] Line 87: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 87: Add missing named argument `deleted` to `RecordModel`
- [x] Line 110: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 110: Add missing named argument `deleted` to `RecordModel`
- [x] Line 132: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 132: Add missing named argument `deleted` to `RecordModel`
- [x] Line 150: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 150: Add missing named argument `deleted` to `RecordModel`

---

## ❗ imednet_sdk/api/subjects.py

- [x] Line 74: Fix return type to `ApiResponse[list[SubjectModel]]`

## ❗ imednet_sdk/api/studies.py

- [x] Line 63: Fix return type to `ApiResponse[list[StudyModel]]`
- [x] Line 87: Fix return type to `ApiResponse[list[dict[Any, Any]]]`

## ❗ imednet_sdk/api/sites.py

- [x] Line 74: Fix return type to `ApiResponse[list[SiteModel]]`

## ❗ imednet_sdk/api/records.py

- [x] Line 83: Fix return type to `ApiResponse[list[RecordModel]]`
- [x] Line 140: Fix return type to `JobStatusModel`

## ❗ imednet_sdk/api/record_revisions.py

- [x] Line 74: Fix return type to `ApiResponse[list[RecordRevisionModel]]`

## ❗ imednet_sdk/api/queries.py

- [x] Line 68: Fix return type to `ApiResponse[list[QueryModel]]`

## ❗ imednet_sdk/api/jobs.py

- [x] Line 46: Fix return type to `JobStatusModel`

## ❗ imednet_sdk/api/intervals.py

- [x] Line 74: Fix return type to `ApiResponse[list[IntervalModel]]`

## ❗ imednet_sdk/api/forms.py

- [x] Line 74: Fix return type to `ApiResponse[list[FormModel]]`

## ❗ imednet_sdk/api/codings.py

- [x] Line 47: Fix return type to `ApiResponse[list[CodingModel]]`

## ❗ imednet_sdk/client.py

- [x] Line 71: Replace `SdkValidationError` with `ValidationError` or define `SdkValidationError`
- [x] Line 357: Guard against `None` when accessing `JSONDecodeError`
- [x] Line 381: Fix `"type[list[T]]" has no attribute "parse_obj"` (adjust annotation or method)
- [ ] Line 590: Fix argument count and types for `build_model_from_variables`
- [ ] Line 614: Fix return type to `ApiResponse[list[Any]]`
- [ ] Line 614: Fix argument 1 type passed to `_fetch_and_parse_typed_records`
- [ ] Line 614: Fix argument 2 type passed to `_fetch_and_parse_typed_records`

## ❗ tests/test_client.py

- [ ] Line 854: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 854: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 872: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 872: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 894: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 894: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 912: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 912: Add missing named argument `deleted` to `RecordModel`
