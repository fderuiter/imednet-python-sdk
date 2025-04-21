# Task 10: Pagination and Iterators

**Objective:** Implement convenient iterator methods for all list endpoints that support pagination, allowing users to easily retrieve all items without manual page handling.

**Definition of Done:**

* All list endpoints supporting pagination are identified.
* A generic helper function/method exists to handle the core pagination logic.
* Iterator methods (e.g., `iter_studies`, `iter_sites`) are implemented for each relevant resource client.
* Iterators correctly fetch subsequent pages using the `pagination` metadata from responses.
* Iterators yield the appropriate Pydantic models.
* Users can specify the page `size` for the underlying requests.
* Iterators handle potential API errors during page traversal gracefully.
* Documentation (Task 8) and examples (Task 8) demonstrate the usage of these iterators.
* (Optional) Convenience methods like `list_all_studies` exist, using the iterators internally.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task, typically focusing on one resource endpoint's iterator (e.g., implement `iter_studies`).
2. **Write/Update Tests (TDD):**
   * Navigate to the relevant test file (e.g., `tests/api/test_studies.py`).
   * Write tests for the new iterator method (e.g., `test_iter_studies`).
   * Use mocking (`requests-mock`) to simulate multi-page responses:
     * Mock a response for page 0 with `currentPage: 0`, `totalPages: 2` (or more), and some `data`.
     * Mock responses for subsequent pages (page 1, page 2, ...) with updated `currentPage` and `data`.
     * Mock the final page response with `currentPage: totalPages - 1`.
   * Assert that the iterator yields the correct number of items across all mocked pages.
   * Assert that the correct Pydantic models are yielded.
   * Assert that the correct query parameters (`page`, `size`, and any others like `filter`, `sort`) are sent for each page request.
   * Test specifying a custom `size` parameter.
   * Test error handling during iteration (e.g., mock an error on page 1).
   * (Optional) Test the `list_all_...` convenience method if implemented.
3. **Implement Code:**
   * Identify the list endpoints needing iterators (Studies, Sites, Forms, Intervals, Records, RecordRevisions, Variables, Codings, Subjects, Users, Visits).
   * Design and implement the core pagination logic (e.g., in `BaseClient` or `imednet_sdk/utils.py`). This might involve a loop checking `currentPage` and `totalPages`.
   * Add the iterator method (e.g., `iter_studies`) to the corresponding resource client (e.g., `StudiesClient`).
   * The iterator method should call the underlying list method (e.g., `list_studies`) repeatedly, updating the `page` parameter based on the pagination logic.
   * Use `yield` or `yield from` to return items from the `data` array of each page's response.
   * Pass through other relevant parameters (`size`, `filter`, `sort`, etc.) to the underlying list method calls.
   * (Optional) Implement the `list_all_...` convenience method by collecting all items from the iterator into a list.
4. **Run Specific Tests:** `pytest tests/api/test_<resource>.py -k test_iter_<resource>`
5. **Debug & Iterate:** Fix iterator logic, pagination handling, or test mocks until specific tests pass.
6. **Run All Module Unit Tests:** `pytest tests/` (Ensure no regressions).
7. **Update Memory File:** Document the pagination helper design, the implemented iterators, and test results in `docs/memory/10_pagination_and_iterators.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Tests (Post-Fix):** `pytest tests/api/test_<resource>.py -k test_iter_<resource>`
12. **Re-run All Module Unit Tests (Post-Fix - Optional):** `pytest tests/`
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/10_pagination_and_iterators.md`
16. **Commit Changes:** `git commit -m "feat(api): add pagination iterator for <resource>"` (Adjust scope and message).

**Sub-Tasks:**

* [ ] **Design Pagination Helper:**
  * [ ] Decide location (`BaseClient` or `utils.py`).
  * [ ] Implement core logic to handle page requests based on `pagination` metadata.
* [ ] **Implement Iterators:**
  * [ ] `iter_studies` (`StudiesClient`)
  * [ ] `iter_sites` (`SitesClient`)
  * [ ] `iter_forms` (`FormsClient`)
  * [ ] `iter_intervals` (`IntervalsClient`)
  * [ ] `iter_records` (`RecordsClient`)
  * [ ] `iter_record_revisions` (`RecordRevisionsClient`)
  * [ ] `iter_variables` (`VariablesClient`)
  * [ ] `iter_codings` (`CodingsClient`)
  * [ ] `iter_subjects` (`SubjectsClient`)
  * [ ] `iter_users` (`UsersClient`)
  * [ ] `iter_visits` (`VisitsClient`)
* [ ] **Implement Tests:**
  * [ ] Add tests for each implemented iterator, covering multi-page scenarios, parameter passing, and error handling.
* [ ] **Update Documentation & Examples (Task 8):**
  * [ ] Document how to use the iterators.
  * [ ] Update/add examples demonstrating iterator usage.
* [ ] **(Optional) Implement `list_all_...` Methods:**
  * [ ] Add convenience methods that return a full list.
  * [ ] Add tests for these methods.
