## 2025-12-11 - Path Traversal in SDK URL Construction
**Vulnerability:** The `_build_path` method in `BaseEndpoint` constructed URLs by joining segments with `/` without encoding them. This allowed path traversal (`../`) and query parameter injection (`?foo=bar`) if user input (like `study_key`) contained these characters.
**Learning:** Even internal helper methods in SDKs must treat inputs as untrusted, especially when constructing URLs. Developers often assume inputs like "IDs" are safe strings, but they can be manipulated to change the request target.
**Prevention:** Always use `urllib.parse.quote` (or equivalent) when inserting dynamic values into URL paths. Ensure `safe=""` is used if slashes should also be encoded to preserve segment boundaries.

## 2025-12-12 - Backslash Injection in Filter Strings
**Vulnerability:** The `build_filter_string` function in `imednet/utils/filters.py` escaped double quotes but not backslashes. This allowed a string ending with a backslash to escape its closing quote (`"..."\`) causing the subsequent part of the filter string to be interpreted as part of the string literal, potentially altering the query logic.
**Learning:** String escaping must always be comprehensive. When generating code or query strings that use backslash escapes, you must escape the escape character itself first.
**Prevention:** Always escape `\` to `\\` before escaping other characters like `"` to `\"` in C-style/JSON-style strings.

## 2025-12-13 - Secrets Leaked in Dataclass Repr
**Vulnerability:** The `Config` class, implemented as a dataclass, automatically generated a `__repr__` method that included all fields, including `api_key` and `security_key`. This meant that logging the config object or printing it during debugging would expose sensitive credentials.
**Learning:** Python dataclasses (and Pydantic models by default) include all fields in their string representation. Convenience features can accidentally defeat security by obscurity/minimization principles.
**Prevention:** Explicitly override `__repr__` (or `__str__`) for any class holding sensitive information. Use a redaction pattern (e.g. `********`) for secret fields.

## 2025-12-14 - Terminal Injection in CLI Output
**Vulnerability:** The CLI displayed user-controlled data (e.g., in tables) using `rich` without escaping. This allowed malicious input containing markup tags (e.g., `[bold red]`) to inject formatting or control sequences into the terminal output, potentially spoofing information or causing confusion.
**Learning:** Terminal output libraries like `rich` often default to interpreting markup for convenience. When displaying untrusted data (from APIs or user input), this feature becomes a liability (similar to XSS in HTML).
**Prevention:** Always explicitly escape untrusted data when rendering to a terminal with rich-text capabilities. Use `rich.markup.escape()` for string values before passing them to display functions.

## 2025-12-15 - CSV Injection in Export
**Vulnerability:** The `records list --output csv` command and `export_to_csv`/`export_to_excel` functions did not sanitize user input before writing to CSV/Excel. Malicious input starting with `=`, `+`, `-`, or `@` could be interpreted as a formula by spreadsheet software (CSV Injection), leading to code execution on the victim's machine.
**Learning:** Exporting user-controlled data to CSV or Excel is not neutral; spreadsheet software interprets specific characters as executable formulas. Standard libraries (`csv`, `pandas`) do not prevent this by default.
**Prevention:** Sanitize all fields in CSV/Excel exports by prefixing risky characters (`=`, `+`, `-`, `@`) with a single quote `'` to force them to be treated as text.
