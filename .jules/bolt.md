## 2025-12-11 - Pydantic Field Validator Introspection Cost
**Learning:** Using `field_validator("*", mode="before")` with runtime type introspection (`get_origin`, `get_args`) for every field in every model instance creates significant overhead (~6x slower than base Pydantic).
**Action:** Cache introspection results (normalization strategies) per field to avoid repeated calculation.
