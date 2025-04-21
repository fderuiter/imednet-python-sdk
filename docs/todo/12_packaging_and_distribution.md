# Task 12: Packaging and Distribution

**Objective:** Prepare the SDK for distribution by configuring the build system, creating package artifacts (sdist, wheel), and setting up the process for publishing to PyPI.

**Definition of Done:**

* `pyproject.toml` (and potentially `setup.cfg`/`setup.py`) is fully configured with project metadata, dependencies, and build backend.
* Source distribution (sdist) and wheel packages build successfully locally (`python -m build`).
* Built packages contain all necessary files (code, README, LICENSE).
* Semantic Versioning (SemVer) is adopted, and a versioning strategy is defined.
* The package can be successfully uploaded to TestPyPI and installed from there.
* A `LICENSE` file is present in the repository root.
* (Optional) A GitHub Actions workflow automates publishing to PyPI on release/tag.

**Workflow Steps:**

1. **Identify Task:** Select a sub-task from the list below (e.g., configure `pyproject.toml`, test build, set up PyPI upload).
2. **Write/Update Tests (TDD - N/A for config, limited for build):**
   * Testing primarily involves running build commands, inspecting package contents, and attempting installation/upload.
3. **Implement Code/Configuration:**
   * Install build tools (`pip install build twine`), add to `requirements-dev.txt`.
   * Configure `pyproject.toml` (build backend, project metadata, dependencies, Python version).
   * (If using setuptools) Configure `setup.cfg` or `setup.py`.
   * Ensure `README.md` is suitable for PyPI description.
   * Add a `LICENSE` file (e.g., MIT, Apache 2.0).
   * Define versioning strategy (e.g., manual bump, use `bump2version`).
   * Create accounts on PyPI/TestPyPI and generate API tokens (store securely, e.g., as GitHub secrets).
   * (Optional) Create GitHub Actions workflow (`.github/workflows/publish.yml`) for automated publishing.
4. **Run Specific Checks:**
   * Build packages: `python -m build`.
   * Check package contents: `tar -tvf dist/*.tar.gz` or `unzip -l dist/*.whl`.
   * Check package metadata: `twine check dist/*`.
   * Upload to TestPyPI: `twine upload --repository testpypi dist/*`.
   * Install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ --no-deps imednet-python-sdk` (or your package name).
   * Run a basic import/usage test after installing from TestPyPI.
   * (Optional) Trigger the publish workflow (e.g., by creating a tag).
5. **Debug & Iterate:** Fix build configurations, metadata, dependencies, version issues, upload credentials, or CI workflow based on errors.
6. **Run All Applicable Checks:**
   * Perform a clean build: `rm -rf dist build *.egg-info && python -m build`.
   * Run `twine check dist/*`.
   * Successfully upload to TestPyPI and install/test from there.
   * (Optional) Ensure the automated publish workflow runs successfully.
7. **Update Memory File:** Document the build system configuration, versioning strategy, PyPI upload process, CI/CD setup (if any), and results in `docs/memory/11_packaging_and_distribution.md`.
8. **Stage Changes:** `git add .`
9. **Run Pre-commit Checks:** `pre-commit run --all-files`.
10. **Fix Pre-commit Issues:** Address any reported issues.
11. **Re-run Specific Checks (Post-Fix):** Verify fixes (Step 4).
12. **Re-run All Applicable Checks (Post-Fix - Optional):** Verify overall integrity (Step 6).
13. **Update Memory File (Post-Fix):** Note any significant fixes.
14. **Stage Changes (Again):** `git add .`
15. **Update Task List:** Mark the completed sub-task checkbox below as done (`[x]`). Stage the change: `git add docs/todo/11_packaging_and_distribution.md`
16. **Commit Changes:** `git commit -m "build: configure packaging"` or `"ci: add publish workflow"` (Adjust type/scope and message).

**Sub-Tasks:**

* [ ] **Configure Build System (`pyproject.toml`, etc.):**
  * [ ] Choose and configure build backend (e.g., `setuptools`, `poetry`).
  * [ ] Add all project metadata (name, version, description, license, etc.).
  * [ ] Specify runtime dependencies and Python version requirement.
* [ ] **Build Packages Locally:**
  * [ ] Run `python -m build`.
  * [ ] Verify sdist and wheel are created in `dist/`.
  * [ ] Inspect package contents.
  * [ ] Run `twine check dist/*`.
* [ ] **Add LICENSE File:**
  * [ ] Choose a license (e.g., MIT).
  * [ ] Add the corresponding `LICENSE` file to the root.
* [ ] **Define Versioning Strategy:**
  * [ ] Decide on manual or automated version bumping.
  * [ ] Set initial version (e.g., `0.1.0`).
* [ ] **TestPyPI Upload:**
  * [ ] Create TestPyPI account and API token.
  * [ ] Upload packages using `twine upload --repository testpypi dist/*`.
  * [ ] Install from TestPyPI and perform a basic check.
* [ ] **Prepare for PyPI Upload:**
  * [ ] Create PyPI account and API token.
  * [ ] Ensure `README.md` renders correctly on PyPI.
* [ ] **(Optional) Automate Publishing (GitHub Actions):**
  * [ ] Create `.github/workflows/publish.yml`.
  * [ ] Configure workflow to trigger on tag/release.
  * [ ] Add steps to build and upload using `twine` and API token (stored as secret).
  * [ ] Consider using PyPI trusted publishing.
* [ ] **Final PyPI Upload (Manual or via CI):**
  * [ ] Upload the final built packages to PyPI.
