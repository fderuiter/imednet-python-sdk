# Task 3: Authentication and Session Management

- Design authentication workflows for API key and security key per Header Reference
- Read credentials from environment variables or config file (`IMEDNET_API_KEY`, `IMEDNET_SECURITY_KEY`)
- Inject headers on each request: `x-api-key`, `x-imn-security-key`, `Accept`, `Content-Type`
- Implement token renewal logic if security key rotates periodically
- Ensure thread-safe session handling with `requests.Session`
- Support custom authentication adapters or credential providers
