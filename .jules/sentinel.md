## 2025-12-11 - Path Traversal in SDK URL Construction
**Vulnerability:** The `_build_path` method in `BaseEndpoint` constructed URLs by joining segments with `/` without encoding them. This allowed path traversal (`../`) and query parameter injection (`?foo=bar`) if user input (like `study_key`) contained these characters.
**Learning:** Even internal helper methods in SDKs must treat inputs as untrusted, especially when constructing URLs. Developers often assume inputs like "IDs" are safe strings, but they can be manipulated to change the request target.
**Prevention:** Always use `urllib.parse.quote` (or equivalent) when inserting dynamic values into URL paths. Ensure `safe=""` is used if slashes should also be encoded to preserve segment boundaries.
