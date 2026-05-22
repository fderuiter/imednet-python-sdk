Streamlit Dashboard Builder Issue Pack
======================================

This guide provides a comprehensive placeholder issue pack for a **standards-guided
clinical reporting workspace** built on Streamlit. The target product is designed for
non-technical clinical users and maps study-specific iMednet records into
CDISC/FDA-aligned reporting objects.

Use this pack with :doc:`issue_management` and :doc:`triage_playbook`.

Product direction (anchor)
--------------------------

Design around canonical reporting outputs first, then map study-specific forms/fields
into those objects.

- Canonical reporting objects (AE/PD/DD) with study mapping underneath
- CDISC-style fields and controlled terminology where applicable
- Regulatory-ready operational summaries and review queues
- Guided, audit-friendly, non-technical workflows

Standards references to keep implementation aligned:

- `CDISC SDTMIG <https://www.cdisc.org/standards/foundational/sdtmig>`__
- `CDISC Controlled Terminology <https://www.cdisc.org/standards/terminology/controlled-terminology>`__
- `FDA Protocol Deviation draft guidance (Dec 2024) <https://www.fda.gov/regulatory-information/search-fda-guidance-documents/protocol-deviations-clinical-investigations-drugs-biological-products-and-devices>`__

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

Architecture layers (scope guardrails)
--------------------------------------

- **Layer A — Raw iMednet records**: top-level metadata plus variable ``recordData``
- **Layer B — Study mapping config**: per-study form/field mapping and value transforms
- **Layer C — Canonical reporting models**: adverse event (AE), protocol deviation (PD),
  and device deficiency/event (DD) records
- **Layer D — Reporting workspace outputs**: dashboards, triage queues, timelines,
  exports, and audit-ready trace views

Epic placeholder
----------------

**Title**
   ``epic(workflows-plugin): deliver standards-guided streamlit clinical reporting workspace``

**Suggested labels**
   ``type:epic``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:xl``, ``risk:high``

**Body (copy/paste)**

.. code-block:: markdown

   ## Objective
   Deliver a study-configurable Streamlit reporting workspace that maps iMednet
   records into canonical AE/PD/DD models and supports CDISC/FDA-aligned review
   workflows for non-technical users.

   ## Product qualities
   - Guided onboarding and setup
   - Trust and explainability for mapped outputs
   - Efficient review workflow and triage
   - Strong usability and accessibility
   - Reliable performance at study scale
   - Governance and audit-readiness
   - Polished user experience (delight)

   ## Scope
   - Study setup wizard + template onboarding
   - Canonical mapping and terminology normalization
   - Standards-aware validation and reportability rules
   - Runtime reporting workspace (dashboards, listings, queues)
   - Configuration persistence/versioning and audit trails
   - Collaboration workflows and review handoffs

   ## Non-goals
   - Fully generic blank-canvas BI builder in MVP
   - Full SDTM submission package generation in MVP
   - Replacing sponsor or CRO quality management systems

   ## Child issues
   - [ ] #<child_issue_1>
   - [ ] #<child_issue_2>
   - [ ] #<child_issue_3>
   - [ ] #<child_issue_4>
   - [ ] #<child_issue_5>
   - [ ] #<child_issue_6>
   - [ ] #<child_issue_7>
   - [ ] #<child_issue_8>
   - [ ] #<child_issue_9>

   ## Acceptance criteria
   - [ ] Workspace supports canonical AE/PD/DD mapping per study
   - [ ] Setup wizard can take a new study from connection to saved profile
   - [ ] Trust panels explain mapping provenance and terminology transforms
   - [ ] Triage workflows support important PD and device-escalation-style review
   - [ ] Configs and review actions are auditable and versioned
   - [ ] Runtime remains usable at target record volumes

Child issue placeholders
------------------------

1) Study setup wizard and guided onboarding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add guided study setup wizard for reporting workspace``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:l``, ``risk:medium``

.. code-block:: markdown

   ## Desired outcome
   Implement a multi-step setup flow:
   1) Connect API
   2) Select study
   3) Scan forms/records
   4) Detect candidate AE/PD/DD forms
   5) Map to canonical fields
   6) Preview outputs
   7) Save study profile

   ## Acceptance criteria
   - [ ] Wizard supports step resume/re-entry
   - [ ] Candidate form detection suggests AE/PD/DD options
   - [ ] Setup ends with saved, reusable study profile

2) Start-from-template onboarding profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add start-from-template reporting profiles``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:low``

.. code-block:: markdown

   ## Desired outcome
   Add profile templates such as:
   - Drug/Biologic Safety Review
   - Protocol Deviation Oversight
   - Device Investigation Review

   ## Acceptance criteria
   - [ ] Template choice pre-populates canonical field expectations
   - [ ] Users can customize template defaults before save
   - [ ] Template metadata is versioned for future updates

3) Canonical mapping + terminology normalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): implement canonical AE/PD/DD mapping and terminology normalization``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:l``, ``risk:high``

.. code-block:: markdown

   ## Desired outcome
   Build mapping from raw study fields to canonical AE/PD/DD objects with configurable
   controlled-terminology normalization for key value sets.

   ## Acceptance criteria
   - [ ] Mapping supports per-domain form and field matching
   - [ ] Normalization dictionaries are configurable per study/profile
   - [ ] Invalid/weak mappings produce actionable warnings

4) Trust layer: provenance, explainability, and quality checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add trust panels for mapping provenance and data quality``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:m``, ``risk:high``

.. code-block:: markdown

   ## Desired outcome
   Add user-facing trust views that show source field lineage, normalization actions,
   missing critical inputs, and confidence/coverage summaries.

   ## Acceptance criteria
   - [ ] Every canonical output field can show source provenance
   - [ ] Data quality checks flag missing required or high-value fields
   - [ ] Users can export trust summaries for review documentation

5) Review workflow, triage queues, and escalations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): implement review queues and standards-guided escalation flags``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:l``, ``risk:high``

.. code-block:: markdown

   ## Desired outcome
   Add review queues and configurable rule flags for expedited safety/compliance review,
   including important protocol deviation candidates and device escalation candidates.

   ## Acceptance criteria
   - [ ] Rules execute on canonical mapped records, not raw fields
   - [ ] Queue filters support role-specific review workflows
   - [ ] Escalation rationale is visible and auditable

6) Runtime usability and accessibility polish
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): improve workspace usability and accessibility for clinical users``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:medium``

.. code-block:: markdown

   ## Desired outcome
   Improve clarity and ease-of-use with plain-language labels, guided empty states,
   keyboard-first interactions, and accessibility improvements.

   ## Acceptance criteria
   - [ ] Empty/error states provide clear next actions
   - [ ] Keyboard navigation works across builder and review tables
   - [ ] Visual terminology is non-technical and role-appropriate

7) Performance and reliability at study scale
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): optimize runtime performance for large study datasets``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p2``, ``status:triage``,
   ``size:m``, ``risk:medium``

.. code-block:: markdown

   ## Desired outcome
   Add pagination, caching, and incremental query patterns to keep dashboards and
   review tables responsive at target record volumes.

   ## Acceptance criteria
   - [ ] Initial load and common filter actions meet agreed response targets
   - [ ] Large result sets are paginated/virtualized
   - [ ] Performance guardrails are covered by automated tests

8) Governance, configuration versioning, and audit trail
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add governed config versioning and audit logging for reporting workspace``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p1``, ``status:triage``,
   ``size:l``, ``risk:high``

.. code-block:: markdown

   ## Desired outcome
   Persist study defaults and optional user overrides with version history, approval
   metadata, and traceable change logs.

   ## Acceptance criteria
   - [ ] Config precedence is explicit (template -> study -> user)
   - [ ] Version rollback is supported with audit metadata
   - [ ] Export/import supports governed promotion across environments

9) Collaboration and handoff workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Title**
   ``feat(workflows-plugin): add reviewer collaboration and handoff features``

**Suggested labels**
   ``type:feature``, ``area:workflows-plugin``, ``priority:p3``, ``status:triage``,
   ``size:s``, ``risk:low``

.. code-block:: markdown

   ## Desired outcome
   Support assignment, watchlists, handoff notes, and review-state transitions so
   coordinators, safety reviewers, and clinical ops can work from a shared workspace.

   ## Acceptance criteria
   - [ ] Review items can be assigned and transitioned through states
   - [ ] Handoff notes are retained with timestamp and actor metadata
   - [ ] Saved filters/views support role-specific daily workflows

Conversion checklist (placeholder -> implementation-ready)
----------------------------------------------------------

- [ ] Title normalized to ``<type>(<area>): <concise outcome>``
- [ ] Parent epic linked via sub-issues
- [ ] Labels set for type, area, priority, status, size, risk
- [ ] Milestone, assignee, and project fields assigned
- [ ] Acceptance criteria are concrete and testable
- [ ] Test impact and docs impact are explicitly stated
- [ ] Compliance/regulatory statements avoid over-claiming MVP scope
- [ ] PR template includes ``Closes #<issue_number>`` linkage
