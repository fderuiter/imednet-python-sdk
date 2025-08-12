# AGENTS.md — imednet/http/

## Responsibilities
HTTP session mgmt, retries, timeouts, error mapping, user-agent.

## Policies
- Default timeouts. Idempotent retries with jitter.
- Respect rate-limit headers. Surface `Retry-After`.
- Map HTTP errors to typed exceptions in `imednet/errors`.

## Tracing
- Optional request/response hooks. Redact sensitive fields.

## Tests
- Retry behavior, timeout, backoff boundaries, 429/5xx handling.
