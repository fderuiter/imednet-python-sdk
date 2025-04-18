<!-- filepath: c:\Users\FrederickdeRuiter\Documents\GitHub\imednet-python-sdk\docs\todo\11_packaging_and_distribution.md -->
# Task 11: Packaging and Distribution

- [ ] **Build System:**
  - [ ] Finalize `pyproject.toml` using a modern build backend like `setuptools` (with `setup.cfg`) or `poetry`.
  - [ ] Ensure all project metadata (name, version, description, author, license, classifiers, keywords, project URLs) is correctly specified.
  - [ ] List all runtime dependencies (e.g., `requests` or `httpx`, `pydantic`) with appropriate version specifiers in `pyproject.toml` (or `setup.cfg`/`setup.py`).
  - [ ] Specify the minimum required Python version.
- [ ] **Source Distribution (sdist) and Wheel:**
  - [ ] Configure the build process to include necessary files (Python code, `README.md`, `LICENSE`).
  - [ ] Test building the sdist and wheel locally (`python -m build`).
  - [ ] Verify the contents of the built packages.
- [ ] **Versioning:**
  - [ ] Adopt Semantic Versioning (SemVer).
  - [ ] Plan for version bumping (manual or automated, e.g., using `bump2version` or similar tools).
- [ ] **PyPI Upload:**
  - [ ] Create accounts on PyPI and TestPyPI.
  - [ ] Generate API tokens for uploading.
  - [ ] Test uploading to TestPyPI (`twine upload --repository testpypi dist/*`).
  - [ ] Install from TestPyPI (`pip install --index-url https://test.pypi.org/simple/ imednet-python-sdk`) and verify basic functionality.
  - [ ] Upload the final package to PyPI (`twine upload dist/*`).
- [ ] **Automation (Optional):**
  - [ ] Create a GitHub Actions workflow for automated publishing to PyPI upon creating a new tag/release.
  - [ ] Use PyPI trusted publishing if possible for enhanced security.
- [ ] **LICENSE File:**
  - [ ] Ensure a `LICENSE` file corresponding to the license specified in `pyproject.toml` is included in the repository root.
