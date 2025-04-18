# Task 10: Pagination and Iterators

- [ ] Identify all list endpoints that support pagination (Studies, Sites, Forms, Intervals, Records, RecordRevisions, Variables, Codings, Subjects, Users, Visits) based on the `pagination` block in their responses. (See `docs/reference/1 common.md` for pagination parameters).
- [ ] Design a helper function or method within `BaseClient` or a dedicated utility module to handle pagination logic.
- [ ] Create generic iterator/generator functions or classes that wrap the list methods (e.g., `list_studies`, `list_sites`).
  - Example signature: `iter_studies(**kwargs) -> Iterator[StudyModel]`
- [ ] The iterator should:
  - Make an initial request to the list endpoint (e.g., `GET /studies?page=0&size=...`).
  - Yield each item from the `data` array of the response.
  - Check the `pagination` block (`currentPage`, `totalPages`).
  - If `currentPage < totalPages - 1`, automatically make subsequent requests for the next page (`page=1`, `page=2`, etc.), passing along any original filter/sort parameters.
  - Continue yielding items until all pages are exhausted.
- [ ] Allow users to specify the `size` parameter for the underlying requests made by the iterator (defaulting to a reasonable value, e.g., 100, up to the max of 500).
- [ ] Ensure the iterator handles potential API errors during page traversal.
- [ ] Provide clear documentation (Task 8) and examples (`examples/`) on how to use these iterators to fetch all items from a paginated endpoint.
- [ ] Consider adding convenience methods like `list_all_studies(**kwargs) -> List[StudyModel]` that use the iterator internally to return a complete list (use with caution for potentially very large datasets).
