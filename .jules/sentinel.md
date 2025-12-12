## 2025-12-11 - Path Traversal in SDK URL Construction
**Vulnerability:** The `_build_path` method in `BaseEndpoint` constructed URLs by joining segments with `/` without encoding them. This allowed path traversal (`../`) and query parameter injection (`?foo=bar`) if user input (like `study_key`) contained these characters.
**Learning:** Even internal helper methods in SDKs must treat inputs as untrusted, especially when constructing URLs. Developers often assume inputs like "IDs" are safe strings, but they can be manipulated to change the request target.
**Prevention:** Always use `urllib.parse.quote` (or equivalent) when inserting dynamic values into URL paths. Ensure `safe=""` is used if slashes should also be encoded to preserve segment boundaries.

## 2025-12-12 - Backslash Injection in Filter Strings
**Vulnerability:** The `build_filter_string` function in `imednet/utils/filters.py` escaped double quotes but not backslashes. This allowed a string ending with a backslash to escape its closing quote (`"..."\`) causing the subsequent part of the filter string to be interpreted as part of the string literal, potentially altering the query logic.
**Learning:** String escaping must always be comprehensive. When generating code or query strings that use backslash escapes, you must escape the escape character itself first.
**Prevention:** Always escape `\` to `\\` before escaping other characters like `"` to `\"` in C-style/JSON-style strings.
