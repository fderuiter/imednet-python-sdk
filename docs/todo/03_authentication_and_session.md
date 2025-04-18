# Task 3: Authentication and Session Management

- [ ] Implement logic within the main client class (or `BaseClient`) to handle authentication credentials.
- [ ] Read API Key and Security Key from environment variables (`IMEDNET_API_KEY`, `IMEDNET_SECURITY_KEY`) AND allow passing them during client initialization.
- [ ] Ensure the `BaseClient` automatically injects the following headers into every request:
  - `x-api-key`
  - `x-imn-security-key`
  - `Accept: application/json`
  - `Content-Type: application/json`
    (Reference: `docs/reference/1 common.md` and `docs/reference/2 header.md`)
- [ ] Validate that keys are provided before making requests; raise an `AuthenticationError` if missing.
- [ ] Consider security implications: avoid logging keys, ensure secure storage if configuration files are used.
- [ ] If using `requests.Session` or `httpx.Client`, ensure session/client instances manage headers correctly across requests.
- [ ] (Future Consideration) If keys rotate or expire, implement logic for renewal (though the current docs don't mention this).
- [ ] Ensure session handling is thread-safe if the client will be used in multi-threaded applications.
