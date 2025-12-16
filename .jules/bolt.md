## 2025-12-11 - Pydantic Field Validator Introspection Cost
**Learning:** Using `field_validator("*", mode="before")` with runtime type introspection (`get_origin`, `get_args`) for every field in every model instance creates significant overhead (~6x slower than base Pydantic).
**Action:** Cache introspection results (normalization strategies) per field to avoid repeated calculation.

## 2025-12-11 - Date Parsing Overhead
**Learning:** Custom ISO 8601 parsing logic (handling 'Z' and padding) was 5x slower than native `datetime.fromisoformat` in Python 3.11+. Since this is used in every API model validation, it's a significant tax.
**Action:** Use `sys.version_info` to leverage native C-implementations where available, while keeping compatibility fallbacks.

## 2025-12-11 - Pydantic Validator Optimization
**Learning:** `JsonModel`'s `_normalise` validator was creating tuples and calling a function on every field of every record. This overhead adds up significantly when processing thousands of records.
**Action:** Changed the internal `_NORMALIZERS` cache to a nested dictionary (`Dict[type, Dict[str, Callable]]`) and accessed it directly in the hot path using `try-except KeyError`, avoiding function call and tuple creation overhead. This resulted in a ~13% speedup in model validation.

## 2025-12-11 - Resolving Method Attributes in Hot Loops
**Learning:** Repeatedly calling `hasattr` and `getattr` (especially with string arguments) in a hot loop (like pagination) adds measurable overhead (~20%). Also, blindly using `getattr(obj, name, default)` can cause eager evaluation bugs if `default` is an expression that accesses attributes.
**Action:** Resolve the method/function outside the loop once. Respect inheritance by checking for overrides before optimizing. Use `getattr` with `None` default and explicit check to avoid eager evaluation risks.

## 2025-12-11 - Regex Compilation in Loops
**Learning:** Compiling regexes inside a function called in a loop (like filter string formatting) adds significant overhead.
**Action:** Pre-compile regexes at the module level.

## 2025-12-11 - Caching String Transformations
**Learning:** Repeatedly transforming the same strings (e.g., snake_case to camelCase for API field names) is wasteful.
**Action:** Use `functools.lru_cache` for pure functions that transform a small set of inputs. This yielded a ~66% speedup in filter string construction.
