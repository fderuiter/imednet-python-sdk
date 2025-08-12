# AGENTS.md — imednet/workflows/

## Purpose
Opinionated, higher-level flows for export, mapping, caching, or multi-step jobs.

## Guardrails
- Do not hide API errors; wrap with clear error types and preserve context.
- Keep I/O pluggable (CSV, SQLite, etc.). Avoid hard-coded paths.

## Validation
- Unit tests for each workflow path, including failure cases.
- Include at least one realistic example under `examples/`.

## Docs
- Short “How-to” snippets in `docs/` for each workflow with CLI or Python usage.
