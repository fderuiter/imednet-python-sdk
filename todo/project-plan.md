# iMednet SDK – Iterative Project Plan

> A lightweight "stage‑gate" roadmap with explicit stop‑checks before you roll forward.

## Project Phases

| Phase | Scope (what you build) | Deliverables (done = …) | Verification Gate (how you prove it) |
|-------|------------------------|-------------------------|------------------------------------|
| **0 · Bootstrap** | - pyproject.toml/Poetry\n- Basic folder skeleton from previous message\n- Pre‑commit hooks: ruff, black, mypy | - Repo compiles (`python -m pip install -e .[dev]` succeeds)\n- `make lint` and `make type` both exit 0 | **Gate 0** – CI run passes on GitHub; skeleton merged to main. |
| **1 · Core Layer** | - core/client.py (retry, back‑off)\n- core/paginator.py\n- core/exceptions.py\n- Unit tests with responses | - 100% branch-cov on core/*\n- Client.get("/health") mocked test green | **Gate 1** – "core" test job in CI ≥ 90% cov and no TODOs left. |
| **2 · Context & Base Endpoint** | - core/context.py\n- endpoints/_base.py using Context | - Switching ctx.study_key changes default params in a test double | **Gate 2** – Property‑based test proves no endpoint uses a None study key when context is set. |
| **3 · Study, Variable, Record Endpoints** | - Concrete endpoint classes\n- models/ dataclasses (Study, Variable, Record)\n- Live‑sandbox integration tests (nightly) | - StudyEndpoint.list() returns ≥ 1 object against sandbox creds | **Gate 3** – Manual QA: run `python -m imednet.scripts.imed studies --limit 5` and eyeball output. |
| **4 · First Workflow – record_mapper** | - workflows/record_mapper.py\n- Docstring example notebook | - Unit test stubs endpoints → DataFrame shape & column names verified | **Gate 4** – Jupyter notebook renders in docs site; reviewer signs off. |
| **5 · Export Bundle Workflow** | - workflows/export_bundle.py (ZIP creation)\n- CLI command imed export-bundle | - Artifact exists at dist/export_date.zip with ≥ 1 CSV | **Gate 5** – Download artifact from CI run, open ZIP, schemas look correct. |
| **6 · Docs & Example Gallery** | - mkdocs‑material site skeleton\n- Two how‑to notebooks (mapper, export) | - mkdocs serve shows nav sidebar; example pages execute via nbsphinx | **Gate 6** – Screenshots shared on PR; doc build job passes. |
| **7 · Packaging & Optional Deps** | - optional-dependencies = { pandas = ... }\n- Wheel & sdist via Poetry | - pip install imednet-sdk==X.Y.Z into fresh venv → import imednet works | **Gate 7** – TestPyPI upload; install log attached to PR comment. |
| **8 · Release 0.1.0** | - CHANGELOG\n- GH release notes\n- Semantic tag v0.1.0 | - Release pipeline publishes to PyPI\n- README badge shows latest version | **Gate 8** – PyPI page accessible; `pip install imednet-sdk` gives 0.1.0. |
| **9 · Backlog Grooming / Next Workflows** | - Define next two workflow tickets (AE linker, query_log) with specs & tests | — | **Exit** – Planning doc accepted by team. |

## How to Run the Project

1. **Time‑boxes** – Each phase is a 1‑ to 3‑day pull request.
2. **Definition of done** = Deliverables and gate passed.
3. **No Gate, no merge** – PR reviewers tick a "Gate complete" checklist before approving.
4. **Artifacts per phase** – Tag branch phase‑n‑complete before you start the next; easy roll‑backs.
5. **CI matrix** – Fast unit tests on every push; nightly "sandbox integration" GitHub Action for live API checks.
6. **Issue templates** – "Feature", "Bug", "Workflow idea"; each gate maps to a checklist section.

> Follow the table row‑by‑row and you'll always know what to build, when to stop, and how to prove you nailed it before moving on.
