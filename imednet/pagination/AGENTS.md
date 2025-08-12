# AGENTS.md — imednet/pagination/

## Purpose
Sync and async iterators for paged endpoints.

## Rules
- Lazy iteration. Bounded memory. Stop cleanly on last page.
- Expose page size and cursor controls.
- Provide `iter_items()` and `iter_pages()` variants.

## Tests
- Large page counts, empty last page, transient error mid-stream.
