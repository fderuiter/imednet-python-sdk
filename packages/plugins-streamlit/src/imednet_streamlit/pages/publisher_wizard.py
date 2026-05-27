"""Publisher Wizard — secure configuration review and production publish flow.

Integrates :class:`~imednet_workflows.config_version_control.ConfigVersionStore`
and :class:`~imednet_workflows.standards_validation.StandardsReadinessValidator`
to present a multi-stage validation checklist before a coordinated publish
sign-off by an authorised role.
"""

from __future__ import annotations

import json
from typing import Any

import streamlit as st

from imednet.models.study_config import StudyConfiguration
from imednet_streamlit.auth import get_study_key
from imednet_workflows.config_version_control import ConfigVersionStore

# ---------------------------------------------------------------------------
# Session-state keys
# ---------------------------------------------------------------------------
_KEY_CONNECTED = "_imednet_connected"
_KEY_USER = "_publisher_user"
_KEY_ROLE = "_publisher_role"
_KEY_COMMIT_ID = "_publisher_commit_id"
_KEY_CONFIG_STORE_PATH = "_publisher_store_path"

_AUTHORIZED_ROLES = frozenset({"manager", "admin"})

_DEFAULT_STORE_PATH = "~/.imednet/config_versions.sqlite3"


def _get_store() -> ConfigVersionStore:
    path = st.session_state.get(_KEY_CONFIG_STORE_PATH, _DEFAULT_STORE_PATH)
    return ConfigVersionStore(db_path=str(path))


def _render_auth_section() -> tuple[str, str]:
    """Render user identity inputs; return (user, role)."""
    st.subheader("🔐 Publisher Identity")
    st.markdown(
        "Enter your identity to authenticate publish actions.  "
        "Only **manager** or **admin** roles may approve and publish."
    )
    col_user, col_role = st.columns(2)
    user = col_user.text_input(
        "Username",
        value=st.session_state.get(_KEY_USER, ""),
        key=_KEY_USER,
    )
    role = col_role.selectbox(
        "Role",
        options=["viewer", "reviewer", "manager", "admin"],
        index=["viewer", "reviewer", "manager", "admin"].index(
            st.session_state.get(_KEY_ROLE, "viewer")
        ),
        key=_KEY_ROLE,
    )
    return user, str(role)


def _render_commit_selector(study_key: str, store: ConfigVersionStore) -> str | None:
    """Render history selector; return selected commit_id or None."""
    st.subheader("📋 Configuration History")
    history = store.get_history(study_key)
    if not history:
        st.info("No committed configuration versions found for this study.")
        return None

    options = [
        f"{entry['version_tag']} — {entry['commit_id'][:12]} by {entry['modified_by']} "
        f"({entry['timestamp'][:19]})"
        for entry in history
    ]
    selected_index = st.selectbox(
        "Select configuration version to publish",
        options=options,
        index=len(options) - 1,
        key="publisher_commit_selector",
    )
    return history[options.index(selected_index)]["commit_id"]


def _render_validation_checklist(
    config: StudyConfiguration,
) -> tuple[bool, dict[str, Any]]:
    """Run validation checks and render interactive checklist.

    Returns:
        A tuple of (all_passed, report_dict).
    """
    st.subheader("✅ Standards-Readiness Checklist")

    report: dict[str, Any] = {}

    # 1. Mapping completeness
    has_mappings = len(config.mappings) > 0
    report["has_mappings"] = has_mappings
    _render_check("Field mappings defined", has_mappings, f"{len(config.mappings)} mapping(s)")

    # 2. Terminology normalization
    has_terminology = len(config.terminology_lookups) > 0
    report["has_terminology"] = has_terminology
    total_terms = sum(len(v) for v in config.terminology_lookups.values())
    _render_check(
        "Terminology normalization rules present",
        has_terminology,
        f"{total_terms} rule(s) across {len(config.terminology_lookups)} domain(s)",
    )

    # 3. Widgets configured
    has_widgets = len(config.widgets) > 0
    report["has_widgets"] = has_widgets
    _render_check("Dashboard widgets configured", has_widgets, f"{len(config.widgets)} widget(s)")

    # 4. Version tag well-formed (semantic-version-like)
    import re

    version_ok = bool(re.match(r"^\d+\.\d+\.\d+", config.version))
    report["version_ok"] = version_ok
    _render_check("Version tag is well-formed", version_ok, f"version = {config.version!r}")

    # 5. Study key present
    study_key_ok = bool(config.study_key)
    report["study_key_ok"] = study_key_ok
    _render_check("Study key is non-empty", study_key_ok, f"studyKey = {config.study_key!r}")

    all_passed = all([has_mappings, has_terminology, has_widgets, version_ok, study_key_ok])
    return all_passed, report


def _render_check(label: str, passed: bool, detail: str) -> None:
    icon = "✅" if passed else "❌"
    st.markdown(f"{icon} **{label}** — {detail}")


def _render_diff_section(
    study_key: str,
    store: ConfigVersionStore,
    target_commit_id: str,
) -> None:
    """Render a historical diff comparison prior to publishing."""
    st.subheader("🔍 Historical Diff")
    history = store.get_history(study_key)
    if len(history) < 2:
        st.info("Not enough history to display a diff.")
        return

    commit_options = [
        f"{e['version_tag']} — {e['commit_id'][:12]} ({e['timestamp'][:19]})" for e in history
    ]
    # Default: compare the previous commit against the target
    target_idx = next(
        (i for i, e in enumerate(history) if e["commit_id"] == target_commit_id),
        len(history) - 1,
    )
    compare_idx = max(0, target_idx - 1)

    col_a, col_b = st.columns(2)
    base_label = col_a.selectbox(
        "Base (before)",
        options=commit_options,
        index=compare_idx,
        key="publisher_diff_base",
    )
    head_label = col_b.selectbox(
        "Head (after)",
        options=commit_options,
        index=target_idx,
        key="publisher_diff_head",
    )

    base_commit = history[commit_options.index(base_label)]["commit_id"]
    head_commit = history[commit_options.index(head_label)]["commit_id"]

    if base_commit == head_commit:
        st.info("Base and Head are the same commit — no differences.")
        return

    try:
        diff = store.diff_configs(base_commit, head_commit)
    except KeyError as exc:
        st.error(f"Unable to compute diff: {exc}")
        return

    added = diff.get("added", {})
    removed = diff.get("removed", {})
    changed = diff.get("changed", {})

    if not added and not removed and not changed:
        st.success("No differences found between the two selected versions.")
        return

    if added:
        st.markdown("**➕ Added keys**")
        st.json(added)
    if removed:
        st.markdown("**➖ Removed keys**")
        st.json(removed)
    if changed:
        st.markdown("**✏️ Changed values**")
        st.json(changed)


def _render_publish_action(
    study_key: str,
    store: ConfigVersionStore,
    commit_id: str,
    config: StudyConfiguration,
    user: str,
    role: str,
    all_checks_passed: bool,
) -> None:
    """Render the approval gate and publish button."""
    st.subheader("🚀 Publish to Production")

    is_authorized = role in _AUTHORIZED_ROLES
    if not is_authorized:
        st.warning(
            f"Role **{role!r}** is not authorised to publish.  "
            "Ask a **manager** or **admin** to perform this action."
        )
        st.button("Approve & Publish to Production", disabled=True, key="publisher_publish_btn")
        return

    if not all_checks_passed:
        st.warning("All validation checks must pass before publishing.")
        st.button("Approve & Publish to Production", disabled=True, key="publisher_publish_btn")
        return

    if not user:
        st.warning("A username is required to record the publish action.")
        st.button("Approve & Publish to Production", disabled=True, key="publisher_publish_btn")
        return

    st.info(
        f"Publishing commit **{commit_id[:12]}** (v{config.version}) "
        f"for study **{study_key}** as **{user}** ({role})."
    )

    if st.button("Approve & Publish to Production", key="publisher_publish_btn"):
        try:
            bumped = StudyConfiguration.model_validate(
                {
                    **config.model_dump(mode="json", by_alias=True),
                    "version": _bump_patch(config.version),
                }
            )
            new_commit_id = store.commit_config(
                study_key=study_key,
                config=bumped,
                user=user,
                desc=f"Published to production by {user} ({role})",
            )
            st.success(
                f"✅ Published successfully.  "
                f"New commit: **{new_commit_id[:12]}** (v{bumped.version})"
            )
            st.session_state[_KEY_COMMIT_ID] = new_commit_id
        except ValueError as exc:
            # Duplicate commit — config is already up-to-date
            st.info(str(exc))
        except Exception as exc:  # pragma: no cover - defensive runtime UI handling
            st.error(f"Publish failed ({type(exc).__name__}): {exc}")


def _bump_patch(version: str) -> str:
    """Increment the patch segment of a semver-like version string."""
    parts = version.split(".")
    if len(parts) >= 3:
        try:
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)
        except ValueError:
            pass
    return version


def render_page() -> None:
    st.title("🏛️ Configuration Publisher Wizard")

    if not st.session_state.get(_KEY_CONNECTED):
        st.info("Please connect from the sidebar before using the publisher.")
        return

    try:
        study_key = get_study_key()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    store = _get_store()

    user, role = _render_auth_section()
    st.divider()

    commit_id = _render_commit_selector(study_key, store)
    if commit_id is None:
        return

    try:
        config = store.rollback_config(study_key, commit_id)
    except KeyError as exc:
        st.error(str(exc))
        return

    st.divider()
    with st.expander("View raw configuration JSON", expanded=False):
        st.json(json.loads(config.model_dump_json(by_alias=True)))

    st.divider()
    _render_diff_section(study_key, store, commit_id)
    st.divider()
    all_passed, _report = _render_validation_checklist(config)
    st.divider()
    _render_publish_action(study_key, store, commit_id, config, user, role, all_passed)


render_page()
