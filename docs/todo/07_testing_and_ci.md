# Task 7: Testing Strategy and Automation

- Define testing pyramid (unit, integration, end-to-end)
- Setup test framework (pytest) and fixtures
- Write unit tests for each resource client method:
  - e.g., test `SitesClient.get_sites` with paging, sorting, filtering using sample JSON from `docs/reference/sites.md`
  - Validate model serialization/deserialization for each Pydantic model (e.g., SiteModel, ErrorModel)
- Use `pytest` fixtures to load sample response files under `tests/fixtures/*` matching reference docs
- Mock external HTTP interactions with `responses` or `requests-mock` to assert headers and query parameters
- Add tests for error conditions based on `1000`, `9001`, and `9000` error payloads
- Create integration tests against a sandbox or recorded VCR cassettes for core flows
- Configure coverage with `pytest-cov` and enforce thresholds (e.g., 90%+)
- Add GitHub Actions workflow (`.github/workflows/ci.yml`) to run tests on Python 3.8–3.11 and report coverage
