# 📝 mypy TODO List

## ✅ imednet_sdk\models\interval.py

- [x] Fix: "classmethod" used with a non-method

## ✅ tests\client\test_get_typed_records.py

- [x] Line 87: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 87: Add missing named argument `deleted` to `RecordModel`
- [x] Line 110: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 110: Add missing named argument `deleted` to `RecordModel`
- [x] Line 132: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 132: Add missing named argument `deleted` to `RecordModel`
- [x] Line 150: Add missing named argument `parentRecordId` to `RecordModel`
- [x] Line 150: Add missing named argument `deleted` to `RecordModel`

## ❗ imednet_sdk\utils.py

- [] Lines 30–47: Fix incompatible types in dict entries (use `type[Any]` instead of typing special forms)
- [] Line 141: Add `list_variables` attribute to `ResourceClient` or fix usage
- [] Line 182: Add `list_records` attribute to `ResourceClient` or fix usage

## ❗ imednet_sdk\api\visits.py

- [ ] Line 47: Fix return type to match `ApiResponse[list[VisitModel]]`

## ❗ imednet_sdk\api\variables.py

- [ ] Line 51: Fix return type to match `ApiResponse[list[VariableModel]]`

## ❗ imednet_sdk\api\users.py

- [ ] Line 54: Fix return type to match `ApiResponse[list[UserModel]]`

## ❗ imednet_sdk\api\subjects.py

- [ ] Line 74: Fix return type to match `ApiResponse[list[SubjectModel]]`

## ❗ imednet_sdk\api\studies.py

- [ ] Line 63: Fix return type to match `ApiResponse[list[StudyModel]]`
- [ ] Line 87: Fix return type to match `ApiResponse[list[dict[Any, Any]]]`

## ❗ imednet_sdk\api\sites.py

- [ ] Line 74: Fix return type to match `ApiResponse[list[SiteModel]]`

## ❗ imednet_sdk\api\records.py

- [ ] Line 83: Fix return type to match `ApiResponse[list[RecordModel]]`
- [ ] Line 140: Fix return type to match `JobStatusModel`

## ❗ imednet_sdk\api\record_revisions.py

- [ ] Line 74: Fix return type to match `ApiResponse[list[RecordRevisionModel]]`

## ❗ imednet_sdk\api\queries.py

- [ ] Line 68: Fix return type to match `ApiResponse[list[QueryModel]]`

## ❗ imednet_sdk\api\jobs.py

- [ ] Line 46: Fix return type to match `JobStatusModel`

## ❗ imednet_sdk\api\intervals.py

- [ ] Line 74: Fix return type to match `ApiResponse[list[IntervalModel]]`

## ❗ imednet_sdk\api\forms.py

- [ ] Line 74: Fix return type to match `ApiResponse[list[FormModel]]`

## ❗ imednet_sdk\api\codings.py

- [ ] Line 47: Fix return type to match `ApiResponse[list[CodingModel]]`

## ❗ imednet_sdk\client.py

- [ ] Line 71: Replace `SdkValidationError` with `ValidationError` or define it
- [ ] Line 254: Fix incompatible assignment type (from `Any | None` to `dict[str, Any]`)
- [ ] Line 331: Guard against `None` for `Future.exception`
- [ ] Line 357: Guard against `None` for `JSONDecodeError`
- [ ] Line 590: Fix argument count and type for `build_model_from_variables`
- [ ] Line 614: Fix return type to match `ApiResponse[list[BaseModel]]`
- [ ] Line 614: Fix argument 1 to `_fetch_and_parse_typed_records` to be `ResourceClient`
- [ ] Line 614: Fix argument 2 to `_fetch_and_parse_typed_records` to be `ResourceClient`

## ❗ tests\test_client.py

- [ ] Line 854: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 854: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 872: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 872: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 894: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 894: Add missing named argument `deleted` to `RecordModel`
- [ ] Line 912: Add missing named argument `parentRecordId` to `RecordModel`
- [ ] Line 912: Add missing named argument `deleted` to `RecordModel`

---

**Total Errors:** 53  
**Files Affected:** 18  
