# Task 09: Documentation and Usage Examples

**Objective:** Create comprehensive documentation (README, Sphinx API reference, usage guides) and practical usage examples for the SDK.

**Definition of Done:**

* `README.md` is updated with a project description, installation instructions, quickstart, authentication info, and a link to full docs.
* Sphinx documentation is set up in `docs/source/`.
* `conf.py` is configured with project details, theme, and necessary extensions.
* `api.rst` uses `sphinx.ext.autodoc` to generate API reference from docstrings.
* Usage guides (`usage.rst`, etc.) cover client initialization, requests, pagination, filtering/sorting, creating resources, and error handling.
* All public modules, classes, and methods in `imednet_sdk/` have comprehensive docstrings (e.g., Google/NumPy style).
* Practical usage examples exist in the `examples/` directory.
* (Optional) CI/CD for building and deploying documentation is configured.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., update README, configure Sphinx, write usage guide).
2. **Write/Update Tests (TDD - N/A for most docs):**
   * Testing for documentation primarily involves building the docs and verifying the output, or running example scripts.
   * For docstrings, ensure they are picked up correctly by Sphinx during the build process.
3. **Implement Code/Content:**
   * Edit `README.md`.
   * Set up Sphinx: Create `docs/source/conf.py`, `index.rst`, `api.rst`, `usage.rst`, etc.
   * Install Sphinx and related extensions (`pip install sphinx sphinx_rtd_theme ...`), add to `requirements-dev.txt`.
   * Write/update docstrings in `imednet_sdk/**/*.py`.
   * Create/update example scripts in `examples/*.py`.
   * (Optional) Create/update CI workflow for docs (`.github/workflows/docs.yml`).
4. **Run Specific Checks:**
   * Build Sphinx docs: `cd docs && make html` (or `sphinx-build -b html source build/html`). Check for build warnings/errors.
   * Review the generated HTML documentation in `docs/build/html/`.
   * Run example scripts: `python examples/<example_name>.py` (ensure they run without errors, potentially with mock credentials/setup).
   * (Optional) Trigger CI workflow for docs.
5. **Debug & Iterate:** Fix docstrings, reStructuredText syntax, Sphinx configuration, example code, or CI workflow based on errors or review.
6. **Run All Applicable Checks:**
   * Re-build all docs: `cd docs && make clean html`.
   * Run all example scripts.
   * Run linters/formatters on code and examples: `pre-commit run --all-files`.
7. **Update Memory File:** Document the documentation structure, Sphinx setup, example scripts created, and build/run results in `docs/memory/08_documentation_and_examples.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files` (May include doc linters if configured).
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Checks (Post-Fix):** Verify fixes (Step 4).
12. **Re-run All Applicable Checks (Post-Fix - Optional):** Verify overall integrity (Step 6).
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/08_documentation_and_examples.md`
16. **Commit Changes:** `git commit -m "docs: <description_of_subtask>"` or `"feat(examples): <description_of_subtask>"` (Adjust type/scope and message).

**Sub-Tasks:**

* [x] **README.md:**
  * [x] Write clear project description.
  * [x] Add installation instructions.
  * [x] Add Quickstart section (initialization, simple call).
  * [x] Explain authentication.
  * [x] Link to full documentation.
* [x] **Sphinx Documentation Setup (`docs/source/`):**
  * [x] Install Sphinx, theme (e.g., `sphinx_rtd_theme`), extensions (`autodoc`, `napoleon`, `viewcode`, `intersphinx`). Add to `requirements-dev.txt`.
  * [x] Configure `conf.py` (project details, theme, extensions).
  * [x] Create basic `index.rst`.
* [ ] **API Reference (`docs/source/api.rst`):**
  * [ ] Use `sphinx.ext.autodoc` (`automodule`, `autoclass`, etc.) to generate reference from docstrings.
  * [ ] Ensure `imednet_sdk` is in the Python path for Sphinx.
* [ ] **Usage Guides (`docs/source/usage.rst`, etc.):**
  * [x] Write guide: Client initialization and authentication.
  * [x] Write guide: Making requests (listing, getting).
  * [x] Write guide: Handling pagination (manual, iterators).
  * [x] Write guide: Filtering and sorting.
  * [x] Write guide: Creating/updating resources.
  * [x] Write guide: Error handling (exceptions).
  * [ ] (Optional) Add explanations of core API concepts.
* [ ] **Docstrings (`imednet_sdk/`):**
  * [ ] Add/update comprehensive docstrings for all public modules, classes, methods, functions (use Google/NumPy style).
* [ ] **Usage Examples (`examples/`):**
  * [ ] Create `examples/list_studies_and_sites.py`.
  * [ ] Create `examples/find_subjects_by_status.py`.
  * [ ] Create `examples/get_all_records_for_subject.py` (using pagination).
  * [ ] Create `examples/create_new_record.py`.
  * [ ] Create `examples/handle_api_errors.py`.
  * [ ] Ensure examples are clear, commented, and runnable.
* [ ] **CI/CD for Docs (Optional):**
  * [ ] Create GitHub Actions workflow to build docs.
  * [ ] Configure hosting (ReadTheDocs, GitHub Pages).
