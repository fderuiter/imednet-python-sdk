# AGENTS.md — imednet/errors/

## Purpose
Exception hierarchy and mapping.

## Layout
- `ImednetError` base.
- `AuthError`, `RateLimitError`, `TimeoutError`, `ApiError(code, details)`.

## Rules
- Human message + machine context. Preserve server payload.
- No secrets in messages.

## Tests
- Mapping table from status codes and error bodies.
