## 2025-12-11 - Pydantic Field Validator Introspection Cost
**Learning:** Using `field_validator("*", mode="before")` with runtime type introspection (`get_origin`, `get_args`) for every field in every model instance creates significant overhead (~6x slower than base Pydantic).
**Action:** Cache introspection results (normalization strategies) per field to avoid repeated calculation.

## 2025-12-11 - Date Parsing Overhead
**Learning:** Custom ISO 8601 parsing logic (handling 'Z' and padding) was 5x slower than native `datetime.fromisoformat` in Python 3.11+. Since this is used in every API model validation, it's a significant tax.
**Action:** Use `sys.version_info` to leverage native C-implementations where available, while keeping compatibility fallbacks.
