## 2024-05-22 - Improved CLI Table Readability
**Learning:** CLI users struggle to parse raw Python objects (lists/dicts) and unformatted booleans/datetimes in tables.
**Action:** Always implement a formatter for table cells that handles booleans (colors), datetimes (ISO/human), and truncates long iterables.

## 2025-12-12 - CLI Loading States
**Learning:** Static "Fetching..." messages make the CLI feel unresponsive during network calls.
**Action:** Use `rich.console.Console.status` (via context manager) for all synchronous blocking calls to provide immediate visual feedback.
