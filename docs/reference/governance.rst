Governance — Trust, Traceability & Audit Trail
===============================================

The governance module provides three core capabilities required for regulated
clinical data environments:

1. :ref:`config-version-control` — immutable, SHA-256-signed study
   configuration history with diff and rollback.
2. :ref:`publisher-wizard` — multi-stage validation checklist and
   security-gated publish workflow.
3. :ref:`data-lineage` — interactive drill-down from aggregated dashboard
   metrics to the underlying raw EDC record payloads.

These features are implemented across two packages:

* ``imednet-workflows`` — the backend ``ConfigVersionStore`` class.
* ``imednet-streamlit`` — the two Streamlit dashboard pages.

.. _config-version-control:

Configuration Version Control
------------------------------

``imednet_workflows.config_version_control`` provides ``ConfigVersionStore``,
a thread-safe SQLite-backed ledger for :class:`~imednet.models.study_config.StudyConfiguration`
versions.

.. rubric:: Key properties

* **Immutability** — commit rows are append-only; no history block can be
  edited or deleted in place.
* **Hash integrity** — each commit is identified by the SHA-256 digest of its
  serialised JSON body.  Attempting to commit an unchanged configuration raises
  ``ValueError``.
* **Rollback safety** — :meth:`~imednet_workflows.config_version_control.ConfigVersionStore.rollback_config`
  is non-destructive; it returns the historical
  :class:`~imednet.models.study_config.StudyConfiguration` without touching
  any existing rows.

.. rubric:: Quick-start

.. testcode::

    from imednet.models.study_config import StudyConfiguration, MappingRule
    from imednet_workflows import ConfigVersionStore

    store = ConfigVersionStore()          # default: ~/.imednet/config_versions.sqlite3

    config = StudyConfiguration(
        studyKey="MY_STUDY",
        mappings=[
            MappingRule(
                domain="AE",
                targetField="aeTerm",
                sourceFormKey="AE_FORM",
                sourceVariableName="ae_term",
            )
        ],
    )

    # Commit a version
    commit_id = store.commit_config(
        study_key="MY_STUDY",
        config=config,
        user="alice",
        desc="Initial mapping configuration",
    )
    print(commit_id)   # SHA-256 hex digest

    # Browse history
    for entry in store.get_history("MY_STUDY"):
        print(entry["version_tag"], entry["commit_id"][:12], entry["timestamp"])

    # Diff two versions
    diff = store.diff_configs(commit_a, commit_b)
    print(diff["added"], diff["removed"], diff["changed"])

    # Rollback (read-only)
    old_config = store.rollback_config("MY_STUDY", commit_id)

.. rubric:: API reference

.. autoclass:: imednet_workflows.config_version_control.ConfigVersionStore
   :members:
   :undoc-members:
   :show-inheritance:

.. _publisher-wizard:

Publisher Wizard (Streamlit page)
----------------------------------

The **Publisher Wizard** (``imednet_streamlit.pages.publisher_wizard``) is a
Streamlit dashboard page that wraps the configuration version control system
with a security-gated publish workflow.

.. rubric:: Workflow stages

1. **Identity** — the user enters a username and selects a role.  Only
   ``manager`` and ``admin`` roles may proceed to publish.
2. **History** — a select box lists all committed versions for the active study
   key.  The user chooses the version to deploy.
3. **Raw JSON viewer** — the full configuration JSON can be inspected in an
   expandable panel.
4. **Historical diff** — a side-by-side diff between any two historical commits
   is rendered before approval.
5. **Standards-readiness checklist** — automated checks verify:

   * Field mappings are defined.
   * Terminology normalisation rules are present.
   * Dashboard widgets are configured.
   * The version tag is well-formed (semver-like).
   * The study key is non-empty.

6. **Approve & Publish** — an authorised user clicks the guarded button.  On
   success a new commit is recorded in the ledger with a bumped patch version,
   providing a full audit trail of the publish event.

.. _data-lineage:

Data Lineage Explorer (Streamlit page)
---------------------------------------

The **Data Lineage Explorer** (``imednet_streamlit.pages.data_lineage``) makes
every aggregated metric traceable back to its source data.

.. rubric:: Three-pane lineage view

Selecting a record index opens a side-by-side view:

* **Left pane** — raw EDC record payload from the local cache database.
  Sensitive field names (``api_key``, ``token``, ``secret``, etc.) are
  automatically redacted before display.
* **Centre pane** — the mapping rules from the active
  :class:`~imednet.models.study_config.StudyConfiguration` that were applied to
  this domain.
* **Right pane** — the structured canonical Pydantic model (``AdverseEvent``,
  ``ProtocolDeviation``, or ``DeviceDeficiency``).

.. rubric:: Credential safety

The lineage view *never* exposes credentials.  The ``_redact_sensitive``
helper strips any dict key whose name contains the substrings ``password``,
``token``, ``secret``, ``api_key``, ``apikey``, ``key``, or ``credential``
before the raw payload is rendered.
