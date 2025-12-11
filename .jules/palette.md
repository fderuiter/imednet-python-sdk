## 2024-05-22 - Improved CLI Table Readability
**Learning:** CLI users struggle to parse raw Python objects (lists/dicts) and unformatted booleans/datetimes in tables.
**Action:** Always implement a formatter for table cells that handles booleans (colors), datetimes (ISO/human), and truncates long iterables.
