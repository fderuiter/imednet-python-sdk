# Task 2: Core HTTP Client Implementation

- Design `BaseClient` class wrapping `requests.Session`
- Implement generic request methods (GET, POST, PUT, DELETE)
- Centralize base URL and path construction
- Integrate retry logic (exponential backoff)
- Handle connection pooling and timeout settings
- Support query parameters and custom headers
- Define interface for pluggable HTTP adapters
