Streamlit Dashboard Builder Issue Pack
======================================

This guide provides placeholder GitHub issues for a configurable Streamlit
Dashboard Builder initiative that targets CDISC/FDA-aligned safety and
compliance outputs. Copy each issue draft into GitHub and tailor labels,
assignees, and acceptance criteria as implementation details evolve.

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

Standards-guided design contract
--------------------------------

Use these architectural layers in issue scope and acceptance criteria:

- **Layer A — Raw iMednet records**: top-level metadata plus variable ``recordData``
- **Layer B — Study mapping config**: per-study form/field mapping and value transforms
- **Layer C — Canonical reporting models**: adverse event (AE), protocol deviation (PD),
  and device deficiency/event (DD) records
- **Layer D — Outputs**: operational dashboards, review listings, and export-readiness views

MVP scope should be phrased as **CDISC-aligned structured extraction and review support**
rather than one-click submission-grade compliance generation.

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
   Deliver a study-configurable Streamlit Dashboard Builder workbench that maps
   study-specific records into canonical adverse event (AE), protocol deviation (PD),
   and device deficiency/event (DD) reporting models aligned to CDISC/FDA concepts.

   ## Scope
   - Study schema profiling for records/forms/keys
   - Semantic mapping from raw `recordData` to canonical AE/PD/DD fields
   - Terminology normalization (for yes/no, seriousness, severity, outcome-style values)
   - Standards-guided builder UX for non-technical users
   - Runtime output surfaces (operational dashboard, review listings, export-readiness preview)
   - Reportability/review flags for safety and compliance triage

   ## Non-goals
   - Full blank-canvas drag-and-drop layout engine in MVP
   - Backend multi-tenant permissions model in MVP
   - Claiming full submission-ready SDTM package generation in MVP

   ## Child issues
   - [ ] #<child_issue_1>
   - [ ] #<child_issue_2>
   - [ ] #<child_issue_3>
   - [ ] #<child_issue_4>
   - [ ] #<child_issue_5>
   - [ ] #<child_issue_6>

   ## Acceptance criteria
   - [ ] MVP supports canonical AE, PD, and DD model mapping per study
   - [ ] Dashboard config is saved and reloaded by study key
   - [ ] Runtime outputs render from saved config without hard-coded form keys
   - [ ] Validation warns on weak/empty field mappings
   - [ ] Reportability/review flags are computed for mapped records
   - [ ] Terminology normalization is visible in export-readiness preview

   ## Dependencies
   - Blocked by: #<blocking_issue_number>
   - Coordinates with: #<related_issue_1>, #<related_issue_2>, #<related_issue_3>

   ## Verification
   - [ ] `poetry run black --check .`
   - [ ] `poetry run isort --check --profile black .`
   - [ ] `poetry run ruff check .`
   - [ ] `poetry run mypy (affected packages)`
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
   `recordData` fields, and sample values per study, with candidate mapping hints
   for canonical AE/PD/DD packages.

   ## Acceptance criteria
   - [ ] Profiling groups records by `formKey`
   - [ ] Profile output includes field presence percentage and sample values
   - [ ] UI can preview profiler output for selected study
   - [ ] Candidate forms are suggested for AE/PD/DD mapping setup

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
   Introduce canonical AE/PD/DD models and a per-study mapping config that
   translates raw fields into standards-aligned reporting fields.

   ## Acceptance criteria
   - [ ] Config supports domain form matching (AE/PD/DD)
   - [ ] Config maps canonical fields (`term`, `serious`, `severity`, dates, outcome, action)
   - [ ] Controlled terminology normalization is configurable for key value sets
   - [ ] Runtime extraction returns normalized records for each configured domain
   - [ ] Invalid mappings produce user-facing warnings

   ## Dependencies
   - Parent epic: #<epic_issue_number>
   - Related: #<related_issue_number>

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
   Implement a standards-guided multi-step flow: study selection, reporting package
   selection, canonical field mapping, terminology normalization, and preview/publish.

   ## Acceptance criteria
   - [ ] Users can select source forms per domain
   - [ ] Users can map canonical fields via plain-language prompts and live previews
   - [ ] Users can normalize raw values into controlled categories
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
   Use saved mappings/layout config to render runtime outputs with template-first
   defaults for operational dashboarding and review workflows.

   ## Acceptance criteria
   - [ ] Runtime reads study config and renders mapped domain metrics and listings
   - [ ] Starter templates exist for safety summary and deviation/device review
   - [ ] Empty/missing config states have guided recovery messages
   - [ ] Export-readiness preview highlights missing required canonical fields

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
   Persist both study mapping config and reporting profile config, with precedence:
   global template -> study default -> user override.

   ## Acceptance criteria
   - [ ] Study defaults persist independently of user overrides
   - [ ] Config versions are tracked for safe updates
   - [ ] Export/import path exists for config portability
   - [ ] Reporting profiles (drug/biologic safety, device investigation, general ops)
         are persisted and selectable per study

6) Reportability and escalation rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add reportability flag rules for mapped safety and compliance records``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:high``

.. code-block:: markdown

   ## Problem
   Teams need triage flags to quickly identify records that require expedited safety
   or compliance review.

   ## Desired outcome
   Add configurable rules that compute review/reportability flags from canonical
   AE/PD/DD records (for example missing critical fields, important deviation
   candidates, and Unanticipated Adverse Device Effect (UADE)-like escalation
   candidates).

   ## Acceptance criteria
   - [ ] Rules run on canonical mapped records, not raw source forms
   - [ ] Rule outputs are visible in review listings and export-readiness preview
   - [ ] Rule logic is configurable by reporting profile

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
