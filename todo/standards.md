iMednet‑SDK · Coding & Quality Standards

A living guideline to keep every file predictable, readable, and testable.

⸻

1  Core style policies

Topic	Rule	Rationale
Formatter	Black (line length = 100)	Zero bikeshedding—formatter is the arbiter.
Linter	Ruff with the following rulesets: pycodestyle, pyflakes, isort, pydocstyle (google style), pep8-naming, flake8-bugbear, flake8-simplify, flake8-annotations, flake8-pytest-style	Fast all‑in‑one tool; catches error‑prone patterns.
Imports	Use isort profile black (already handled by Ruff) and absolute imports inside the imednet package. Never use “. relative” beyond same‑package sub‑modules.	Avoid circular‑import surprises; traceability.
Type hints	100 % public‑surface coverage, 90 % internal. Enforce with mypy –strict (allow‑lists by module are OK temporarily).	IDE friendliness, refactor safety.
Docstrings	Public methods & all workflow functions follow Google style (Args:, Returns:, Raises:). Single‑line docstring is fine for trivial internal helpers.	Generates clear MkDocs API pages.
Naming	PascalCase classes & exceptions; snake_case for everything else; modules are singular (record.py, not records.py) except package‐level “collections” folders (endpoints/).	Consistent mental model.
Constants	UPPER_SNAKE_CASE at module top; export only via __all__ when intended for users.	Explicit public contract.
Functions	≤ 50 logical lines where sensible. If longer, extract helpers or move business logic into a workflow module.	Easier code review and reuse.
Exceptions	Never raise bare Exception. Derive from project‑level ImednetError. Prefer Fail Fast—validate args early.	Predictable error tree for SDK clients.
Logging	Use stdlib logging; default level WARNING. Never use print() inside library code. CLI wrappers may print.	Respect host application logging config.



⸻

2  Tooling configuration snippets

pyproject.toml

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.ruff]
line-length = 100
select = [
  "E", "F", "I",         # pycodestyle/pyflakes/isort
  "D",                   # pydocstyle
  "B",                   # bugbear
  "S",                   # flake8-simplify
  "ANN",                 # annotations
  "N",                   # pep8-naming
  "PT",                  # pytest-style
]
ignore = ["D401"]        # allow imperative one‑line summaries
src = ["imednet"]

[tool.mypy]
python_version = "3.10"
strict = true
show_error_codes = true
exclude = ["tests/"]
plugins = []

.pre‑commit‑config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks: [ {id: black} ]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.2
    hooks: [ {id: ruff} ]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: ["pandas-stubs"]

pre‑commit install once; CI will run the same hooks.

⸻

3  Testing conventions

Aspect	Guidance
Framework	pytest with pytest-cov & pytest‑asyncio if we add async endpoints.
Structure	tests/unit/, tests/integration/, tests/workflow/. Mirror package names (tests/unit/endpoints/test_study.py).
Fixtures	Put re‑usable HTTP mocks in tests/conftest.py. Use responses (sync) or respx (async).
Factories	Prefer pydantic_factories or model_bakery over manual dicts.
Assertions	Single assert per branch of behaviour; for DataFrames use pandas.testing.assert_frame_equal.
Coverage thresholds	core/ & endpoints/ ≥ 90 %, repository total ≥ 85 %. Failing the threshold blocks merge.
Naming	Test functions start with test_. Context in given/when/then comments is encouraged.



⸻

4  Git hygiene
	•	Branch model – GitHub flow (main protected, feature branches per PR).
	•	Commit messages – Conventional Commits subset:
	•	feat:, fix:, docs:, refactor:, test:, chore:
	•	Scope optional (feat(workflow): …).
	•	Body explains why, not what (code already shows what).
	•	Pull‑request checklist (enforced by template):
	1.	Lint & type‑check pass locally
	2.	Tests added/updated
	3.	Docs updated (if public surface changed)
	4.	Added to CHANGELOG.md (Unreleased)

⸻

5  Documentation rules
	•	Public APIs must have docstrings that render well in MkDocs.
	•	Examples go in examples/ as executed Jupyter notebooks. They double as integration tests via pytest --nbmake.
	•	CHANGELOG.md follows Keep a Changelog format. Every merged PR that changes behaviour updates the Unreleased section.

⸻

6  Continuous Integration
	•	Matrix: 3.10, 3.11, 3.12
	•	Jobs (fast → slow):
	1.	lint – ruff, black --check, commit‑message lint
	2.	types – mypy strict
	3.	unit – pytest unit with coverage
	4.	integration (nightly) – requires IMEDNET sandbox keys
	5.	docs – build MkDocs; fail on broken links or rst errors
	•	Fail‑fast config; later jobs cancelled if an earlier one fails.

⸻

7  Release checklist (maintainers)
	1.	Update version in imednet/__init__.py & pyproject.toml.
	2.	CHANGELOG.md – move Unreleased → version header.
	3.	Tag vX.Y.Z and push; CI publishes to TestPyPI then PyPI.
	4.	Verify install from PyPI in fresh venv (pip install imednet-sdk==X.Y.Z).
	5.	Create GitHub Release with autogenerated notes.

⸻

How to adopt these standards
	1.	Add the configs above now; run pre-commit install.
	2.	Touch any file → save → Black formats, Ruff + mypy tell you issues.
	3.	CI mirrors local hooks—no “works on my machine” surprises.

Keep the guideline file (docs/dev/coding‑standards.md) in‑repo and evolve via PR like any code.