# iMednet-SDK v1.0 Inventory

> Every folder and file your `iMednet-SDK` repo is likely to contain when v1.0 ships, with a one-sentence purpose statement for each. Use it as a map while you grow the codebase.

imednet-sdk/                         ← project root
│
├── imednet/                         ← importable package
│   ├── init.py                  ← exports ImednetSDK and version
│   │
│   ├── core/                        ← transport + shared plumbing
│   │   ├── init.py              ← re-exports Client, Context, etc.
│   │   ├── client.py                ← HTTP wrapper (retry/back-off, headers)
│   │   ├── context.py               ← Mutable Context (default study_key, etc.)
│   │   ├── paginator.py             ← Generator that automates Mednet paging
│   │   └── exceptions.py            ← Typed error hierarchy (ImednetError → …)
│   │
│   ├── endpoints/                   ← thin facades over REST collections
│   │   ├── init.py
│   │   ├── coding.py                 ← /studies
│   │   ├── form.py              ← /forms
│   │   ├── interval.py                ← /intervals
│   │   ├── job.py                  ← /jobs
│   │   ├── query.py                 ← /queries
│   │   ├── record_revision.py              ← /record_revisions
│   │   ├── record.py                ← /records
│   │   ├── site.py                  ← /sites
│   │   ├── study.py                ← /studies
│   │   ├── user.py                  ← /users
│   │   ├── variable.py                ← /variables
│   │   └── visit.py                 ← /visits
│   │
│   ├── models/                      ← dataclasses / pydantic schemas (built out)
│   │   ├── init.py
│   │   ├── study.py                 ← Study(id, key, name, type, …)
│   │   ├── variable.py              ← Variable(meta fields)
│   │   ├── record.py                ← Dynamic record values + metadata
│   │   ├── site.py                  ← Site(id, name, country, …)
│   │   ├── study.py                 ← Study(id, key, name, type, …)
│   │   ├── variable.py              ← Variable(meta fields)
│   │   ├── record.py                ← Dynamic record values + metadata
│   │   ├── site.py                  ← Site(id, name, country, …)
│   │   └── query.py                 ← Query(id, status, field, …)
│   │
│   ├── workflows/                   ← cross-endpoint “recipes”
│   │   ├── init.py
│   │   ├── record_mapper.py         ← Variables → Records → tidy DataFrame
│   │   ├── export_bundle.py         ← Full-study ZIP of CSV/Parquet + dictionary
│   │   ├── crf_progress.py          ← % complete & open queries per form/site
│   │   ├── query_log.py             ← Flatten audit/query trail to DataFrame
│   │   ├── snapshot_diff.py         ← Compare two exports, show changed rows
│   │   └── lab_normalizer.py        ← Convert units, flag out-of-range labs
│   │
│   ├── utils/                       ← generic helpers, no HTTP
│   │   ├── init.py
│   │   ├── filters.py               ← Build Mednet filter query strings
│   │   ├── dates.py                 ← ISO ↔ datetime helpers, TZ handling
│   │   └── typing.py                ← Common type aliases (JSONDict, DF, …)
│   │
│   ├── sdk.py                       ← High-level façade wiring endpoints + workflows
│   └── cli.py                       ← imed console entry-point (Typer/Rich)
│
├── scripts/                         ← optional extra CLI utilities / one-offs
│   └── clone_site.py                ← Example: bulk-clone subjects between sites
│
├── examples/                        ← executed Jupyter notebooks, rendered in docs
│   ├── 01_quick_start.ipynb         ← Hello-world walkthrough
│   ├── 02_mapper_demo.ipynb         ← Using record_mapper
│   └── 03_export_bundle.ipynb       ← End-to-end data dump
│
├── tests/                           ← pytest suite
│   ├── unit/                        ← fast, mocked HTTP
│   │   ├── test_client.py
│   │   ├── test_paginator.py
│   │   └── endpoints/
│   ├── workflow/                    ← DataFrame equality, snapshot tests
│   └── integration/                 ← live sandbox creds (nightly CI)
│
├── docs/                            ← mkdocs-material documentation
│   ├── index.md                     ← Home page
│   ├── api/                         ← Auto-generated from docstrings
│   └── how-tos/                     ← Markdown + embedded notebook outputs
│
├── .github/
│   └── workflows/
│       ├── ci.yml                   ← lint + type + test matrix on push
│       ├── nightly-integration.yml  ← runs integration suite at 02:00 UTC
│       └── docs.yml                 ← deploys docs to GitHub Pages
│
├── .pre-commit-config.yaml          ← Black, Ruff, MyPy hooks
├── pyproject.toml                   ← Poetry config + tool settings
├── poetry.lock
├── CHANGELOG.md                     ← Keep-a-Changelog format
├── README.md                        ← Badges, install, quick code sample
└── LICENSE

---

## Quick Purpose Glossary

| Folder / File               | Purpose                                                                                                         |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------|
| **core/**                   | Everything about talking to the API: common headers, retry logic, shared exceptions.                            |
| **endpoints/**              | One class per Mednet collection; stays thin—just request/response translation.                                   |
| **models/**                 | Source-of-truth for response/record structure; reused by endpoints and workflows.                              |
| **workflows/**              | Opinionated helpers that orchestrate several endpoints to solve real-world tasks (exports, mapping, diffing).   |
| **utils/**                  | Pure functions used by multiple layers but with no external side-effects.                                       |
| `sdk.py`                    | The public “one object to rule them all”: wires `Client` + `Context` + Endpoints + Workflows.                  |
| `cli.py`                    | Turns common workflows into `imed <sub-command>` UX for non-Python users.                                       |
| **scripts/**                | Ad-hoc utilities you don’t want in the library API but still useful to ship.                                    |
| **examples/**               | Living tutorials; executed during doc build to prevent bit-rot.                                                  |
| **tests/**                  | Confidence net: unit (fast), workflow (medium), integration (slow/nightly).                                     |
| **docs/**                   | Developer & user documentation site—auto-deployed.                                                              |
| **.github/workflows/**      | CI/CD pipelines: lint/type/test, publish docs, publish package.                                                |
| **.pre-commit-config.yaml** | Ensures every commit is formatted, linted, and type-checked locally before push.                                |
| **pyproject.toml**          | Single source for dependencies, build metadata, and tool configs.                                              |

---

_With this structure you can add new endpoints or workflows without touching unrelated code, keep docs and tests alongside features, and ship a maintainable SDK your users trust._  
