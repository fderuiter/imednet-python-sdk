# AGENTS.md — imednet/auth/

## Scope
Token acquisition, refresh, storage.

## Security
- Never log secrets. Mask tokens in errors.
- Read creds from env or config objects. No global state.

## Contracts
- Pluggable auth backends (api key, OAuth2, etc.) via small interfaces.
- Thread-safe and async-safe.

## Tests
- Expiry/refresh races, clock skew, bad creds, retry/backoff.
