## 2025-12-11 - Pydantic Field Validator Introspection Cost
**Learning:** Using `field_validator("*", mode="before")` with runtime type introspection (`get_origin`, `get_args`) for every field in every model instance creates significant overhead (~6x slower than base Pydantic).
**Action:** Cache introspection results (normalization strategies) per field to avoid repeated calculation.

## 2025-12-11 - Date Parsing Overhead
**Learning:** Custom ISO 8601 parsing logic (handling 'Z' and padding) was 5x slower than native `datetime.fromisoformat` in Python 3.11+. Since this is used in every API model validation, it's a significant tax.
**Action:** Use `sys.version_info` to leverage native C-implementations where available, while keeping compatibility fallbacks.

## 2025-12-11 - Pydantic Validator Optimization
**Learning:** `JsonModel`'s `_normalise` validator was creating tuples and calling a function on every field of every record. This overhead adds up significantly when processing thousands of records.
**Action:** Changed the internal `_NORMALIZERS` cache to a nested dictionary (`Dict[type, Dict[str, Callable]]`) and accessed it directly in the hot path using `try-except KeyError`, avoiding function call and tuple creation overhead. This resulted in a ~13% speedup in model validation.
