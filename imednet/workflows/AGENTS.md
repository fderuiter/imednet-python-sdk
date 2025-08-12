# AGENTS.md — imednet/workflows/

## Purpose
Higher-level orchestration over SDK: batching, pagination, retries, transforms.

## Rules
- Fail loud with clear custom errors; preserve server payloads.
- Keep I/O pluggable via interfaces; avoid hard-coded paths.
- No hidden network calls; accept an injected client.

## Validate
- Unit tests for success and error paths.
- Example script under `examples/`.
- Same root checks as core.

## Docs
Add a short how-to page with minimal runnable snippet.
