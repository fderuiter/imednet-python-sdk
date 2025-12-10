## 2024-05-22 - [CLI List Visualization]
**Learning:** Raw lists of Pydantic models in CLI output are unreadable strings.
**Action:** Use `rich.table.Table` with automatic header extraction (from `model_dump()`) to create readable, tabular output for all list commands. Fallback to `print()` for primitives.
