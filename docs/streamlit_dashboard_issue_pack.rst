Streamlit Dashboard Builder Issue Pack
======================================

This guide provides placeholder GitHub issues for the configurable Streamlit
Dashboard Builder initiative. Copy each issue draft into GitHub and tailor
labels, assignees, and acceptance criteria as implementation details evolve.

Use this pack with :doc:`issue_management` and :doc:`triage_playbook`.

How to use this pack
--------------------

For each draft issue:

1. Create the issue with the suggested title format.
2. Apply labels from ``type:*``, ``area:*``, ``priority:*``, ``status:*``, and ``size:*``.
3. Add assignees, milestone, and project fields.
4. Link child issues to the epic using GitHub sub-issues.
5. Keep PRs linked with ``Closes #<issue_number>``.

Recommended native GitHub features
----------------------------------

- **Issue type**: Epic or Task
- **Sub-issues**: Parent epic tracks linked child execution issues
- **Task lists**: Track acceptance criteria and rollout checkpoints
- **Labels**: Type, area, priority, status, size, risk
- **Milestones**: Group phased delivery (MVP, Builder v1, Hardening)
- **Projects**: Use fields for owner, target sprint, and dependency state
- **Saved replies/checklists**: Standardize triage and review comments

Epic placeholder
----------------

**Title**
   ``epic(workflows-plugin): build study-configurable streamlit dashboard builder``

**Suggested labels**
   ``type:epic``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:xl``, ``risk:medium``

**Body (copy/paste)**

.. code-block:: markdown

   ## Objective
   Deliver a study-configurable Streamlit Dashboard Builder that maps study-specific
   record data into normalized dashboard domains (AE/PD/DD + custom domains).

   ## Scope
   - Study schema profiling for records/forms/keys
   - Semantic mapping from raw `recordData` to canonical fields
   - Builder UX to configure mappings and generate dashboards
   - Runtime dashboard rendering from saved configuration

   ## Non-goals
   - Full blank-canvas drag-and-drop layout engine in MVP
   - Backend multi-tenant permissions model in MVP

   ## Child issues
   - [ ] #<child_issue_1>
   - [ ] #<child_issue_2>
   - [ ] #<child_issue_3>
   - [ ] #<child_issue_4>
   - [ ] #<child_issue_5>

   ## Acceptance criteria
   - [ ] MVP supports AE, PD, and DD domain mapping per study
   - [ ] Dashboard config is saved and reloaded by study key
   - [ ] Runtime dashboard renders from saved config without hard-coded form keys
   - [ ] Validation warns on weak/empty field mappings

   ## Dependencies
   - Blocked by: #915
   - Coordinates with: #1005, #1006, #1007

   ## Verification
   - [ ] `poetry run black --check .`
   - [ ] `poetry run isort --check --profile black .`
   - [ ] `poetry run ruff check .`
   - [ ] `poetry run mypy packages/plugins-streamlit/src/imednet_streamlit`
   - [ ] `poetry run pytest -q`
   - [ ] `make docs` (if docs changed)

Child issue placeholders
------------------------

1) Extraction model and schema profiling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add schema profiler for streamlit records builder``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:medium``

.. code-block:: markdown

   ## Problem
   Dashboard logic currently depends on fixed assumptions about forms/fields.

   ## Desired outcome
   Add a schema profiling service that summarizes form keys, record counts, observed
   `recordData` fields, and sample values per study.

   ## Acceptance criteria
   - [ ] Profiling groups records by `formKey`
   - [ ] Profile output includes field presence percentage and sample values
   - [ ] UI can preview profiler output for selected study

   ## Test impact
   Add unit tests for profiler aggregation and edge cases (empty records, sparse fields).

   ## Docs impact
   Add builder setup and profiler usage notes to plugin docs.

2) Semantic mapping and normalized event model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add study-level semantic mapping for dashboard domains``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:l``, ``risk:medium``

.. code-block:: markdown

   ## Problem
   Raw `recordData` keys vary by study, so AE/PD/DD dashboards cannot rely on static
   field names.

   ## Desired outcome
   Introduce a normalized event model and per-study mapping config translating raw
   fields into canonical dashboard fields.

   ## Acceptance criteria
   - [ ] Config supports domain form matching (AE/PD/DD)
   - [ ] Config maps canonical fields (`term`, `serious`, `severity`, etc.)
   - [ ] Runtime extraction returns normalized records for each configured domain
   - [ ] Invalid mappings produce user-facing warnings

   ## Dependencies
   - Parent epic: #<epic_issue_number>
   - Related: #1007

3) Builder UX (guided mapping)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add guided streamlit dashboard builder flow``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:l``, ``risk:medium``

.. code-block:: markdown

   ## Problem
   Non-technical users need guided configuration rather than manual JSON/path editing.

   ## Desired outcome
   Implement a multi-step builder flow: Study selection, domain selection, field mapping,
   and preview/publish.

   ## Acceptance criteria
   - [ ] Users can select source forms per domain
   - [ ] Users can map canonical fields via dropdowns with live previews
   - [ ] Builder validates obvious mapping mistakes before save
   - [ ] Saved config can be edited later

4) Runtime dashboard rendering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): render streamlit dashboards from saved study config``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:medium``

.. code-block:: markdown

   ## Problem
   Current pages are placeholders and do not render config-driven study dashboards.

   ## Desired outcome
   Use saved mappings/layout config to render runtime KPI/chart/table views with
   template-first defaults.

   ## Acceptance criteria
   - [ ] Runtime reads study config and renders mapped domain metrics
   - [ ] Starter templates exist for safety summary (AE/PD/DD)
   - [ ] Empty/missing config states have guided recovery messages

5) Configuration persistence and governance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): persist streamlit dashboard configs with study defaults and user overrides``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p3``, ``status:triage``,
   ``size:m``, ``risk:medium``

.. code-block:: markdown

   ## Problem
   Dashboard mappings and layout choices need stable per-study persistence with optional
   user-specific overrides.

   ## Desired outcome
   Persist extraction/layout configs with precedence: global template -> study default
   -> user override.

   ## Acceptance criteria
   - [ ] Study defaults persist independently of user overrides
   - [ ] Config versions are tracked for safe updates
   - [ ] Export/import path exists for config portability

Development workflow checklist
------------------------------

Use this checklist when moving placeholders into implementation-ready issues:

- [ ] Title normalized to ``<type>(<area>): <concise outcome>``
- [ ] Parent epic linked via sub-issues
- [ ] Labels set for type, area, priority, status, size, risk
- [ ] Milestone, assignee, and project fields assigned
- [ ] Acceptance criteria are testable
- [ ] Test impact and docs impact are explicitly stated
- [ ] PR template includes ``Closes #<issue_number>`` linkage
