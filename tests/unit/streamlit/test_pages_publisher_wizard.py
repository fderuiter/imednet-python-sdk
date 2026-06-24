"""Unit tests for the Publisher Wizard Streamlit page."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from imednet.models.study_config import MappingRule, StudyConfiguration, WidgetConfig
from imednet_workflows.config_version_control import ConfigVersionStore

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = (
    REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"
)
PAGE_PATH = PACKAGE_ROOT / "pages" / "publisher_wizard.py"
MODULE_NAME = "imednet_streamlit.pages.publisher_wizard"


def _make_committed_store(
    tmp_path: Path, study_key: str = "STUDY-01"
) -> ConfigVersionStore:
    """TODO: Add docstring."""
    store = ConfigVersionStore(db_path=tmp_path / "versions.sqlite3")
    config = StudyConfiguration(
        version="1.0.0",
        studyKey=study_key,
        mappings=[
            MappingRule(
                domain="AE",
                targetField="aeTerm",
                sourceFormKey="AE_FORM",
                sourceVariableName="ae_term",
            )
        ],
        terminologyLookups={"AE.aeTerm": {"mild": "MILD"}},
        widgets=[
            WidgetConfig(
                widgetId="w1", type="kpi_card", title="AE", domain="AE", layoutCols=6
            )
        ],
    )
    store.commit_config(study_key, config, user="alice", desc="initial")
    return store


class _FakeContextManager:
    """TODO: Add docstring."""

    def __enter__(self) -> "_FakeContextManager":
        """TODO: Add docstring."""
        return self

    def __exit__(self, *args: Any) -> None:
        """TODO: Add docstring."""
        pass


class _FakeStreamlit:
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.session_state: dict[str, Any] = {"_imednet_connected": True}
        self.success_calls: list[str] = []
        self.warning_calls: list[str] = []
        self.info_calls: list[str] = []
        self.error_calls: list[str] = []
        self.button_presses: set[str] = set()
        self.selectbox_values: dict[str, Any] = {}
        self.text_input_values: dict[str, str] = {}

    def title(self, value: str) -> None:
        """TODO: Add docstring."""
        pass

    def subheader(self, value: str) -> None:
        """TODO: Add docstring."""
        pass

    def markdown(self, value: str, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def info(self, value: str) -> None:
        """TODO: Add docstring."""
        self.info_calls.append(value)

    def success(self, value: str) -> None:
        """TODO: Add docstring."""
        self.success_calls.append(value)

    def warning(self, value: str) -> None:
        """TODO: Add docstring."""
        self.warning_calls.append(value)

    def error(self, value: str) -> None:
        """TODO: Add docstring."""
        self.error_calls.append(value)

    def divider(self) -> None:
        """TODO: Add docstring."""
        pass

    def json(self, value: Any) -> None:
        """TODO: Add docstring."""
        pass

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def button(self, label: str, **kwargs: Any) -> bool:
        """TODO: Add docstring."""
        key = str(kwargs.get("key") or label)
        if kwargs.get("disabled", False):
            return False
        return key in self.button_presses

    def columns(self, spec: Any) -> list[_FakeContextManager]:
        """TODO: Add docstring."""
        count = spec if isinstance(spec, int) else len(spec)
        cols = [_FakeContextManager() for _ in range(count)]
        # Attach button and other widget methods to each column
        for col in cols:
            col.button = self.button  # type: ignore[attr-defined]
            col.metric = self.metric  # type: ignore[attr-defined]
            col.text_input = self.text_input  # type: ignore[attr-defined]
            col.selectbox = self.selectbox  # type: ignore[attr-defined]
        return cols

    def selectbox(
        self, label: str, options: list[Any], index: int = 0, **kwargs: Any
    ) -> Any:
        """TODO: Add docstring."""
        key = str(kwargs.get("key") or label)
        if key in self.selectbox_values and self.selectbox_values[key] in options:
            return self.selectbox_values[key]
        return options[index]

    def text_input(self, label: str, **kwargs: Any) -> str:
        """TODO: Add docstring."""
        key = str(kwargs.get("key") or label)
        if key in self.text_input_values:
            return self.text_input_values[key]
        return str(kwargs.get("value", ""))

    def text_area(self, label: str, **kwargs: Any) -> str:
        """TODO: Add docstring."""
        return str(kwargs.get("value", ""))

    def expander(self, label: str, **kwargs: Any) -> _FakeContextManager:
        """TODO: Add docstring."""
        return _FakeContextManager()

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        """TODO: Add docstring."""
        pass

    def caption(self, value: str) -> None:
        """TODO: Add docstring."""
        pass

    def progress(self, value: float) -> None:
        """TODO: Add docstring."""
        pass


def _run_publisher_wizard(
    fake_st: _FakeStreamlit,
    store: ConfigVersionStore,
    *,
    study_key: str = "STUDY-01",
) -> None:
    """TODO: Add docstring."""
    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "subheader",
        "markdown",
        "info",
        "success",
        "warning",
        "error",
        "button",
        "columns",
        "selectbox",
        "text_input",
        "text_area",
        "divider",
        "json",
        "dataframe",
        "expander",
        "metric",
        "caption",
        "progress",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_study_key = lambda: study_key  # type: ignore[attr-defined]

    class FakeAuth:
        """TODO: Add docstring."""

        def get_user_roles(self):
            """TODO: Add docstring."""
            # Read from session state simulator instead of UI
            return [fake_st.selectbox_values.get("_publisher_role", "viewer")]

        def get_user_id(self):
            """TODO: Add docstring."""
            return fake_st.text_input_values.get("_publisher_user", "")

    class FakeSDK:
        """TODO: Add docstring."""

        auth = FakeAuth()

    fake_auth_module.get_sdk = lambda: FakeSDK()  # type: ignore[attr-defined]

    # Patch ConfigVersionStore so the page uses our test store
    fake_vcm = ModuleType("imednet_workflows.config_version_control")
    fake_vcm.ConfigVersionStore = lambda **kwargs: store  # type: ignore[attr-defined]

    saved: dict[str, Any] = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_workflows.config_version_control",
            MODULE_NAME,
        )
    }
    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_workflows.config_version_control"] = fake_vcm
        module_spec = importlib.util.spec_from_file_location(MODULE_NAME, PAGE_PATH)
        assert module_spec is not None and module_spec.loader is not None
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[MODULE_NAME] = module
        module_spec.loader.exec_module(module)
    finally:
        for key, original in saved.items():
            if original is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = original


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_publisher_wizard_not_connected(tmp_path: Path) -> None:
    """Page shows info message when not connected."""
    store = _make_committed_store(tmp_path)
    fake_st = _FakeStreamlit()
    fake_st.session_state["_imednet_connected"] = False
    _run_publisher_wizard(fake_st, store)
    assert any("connect" in msg.lower() for msg in fake_st.info_calls)


def test_publisher_wizard_empty_history(tmp_path: Path) -> None:
    """Page shows info message when there is no history."""
    store = ConfigVersionStore(db_path=tmp_path / "empty.sqlite3")
    fake_st = _FakeStreamlit()
    _run_publisher_wizard(fake_st, store)
    assert any("no committed" in msg.lower() for msg in fake_st.info_calls)


def test_publisher_wizard_renders_with_history(tmp_path: Path) -> None:
    """Page renders successfully when history exists."""
    store = _make_committed_store(tmp_path)
    fake_st = _FakeStreamlit()
    # No errors expected
    _run_publisher_wizard(fake_st, store)
    assert fake_st.error_calls == []


def test_publisher_wizard_unauthorized_role_blocked(tmp_path: Path) -> None:
    """Users with 'viewer' role cannot publish."""
    store = _make_committed_store(tmp_path)
    fake_st = _FakeStreamlit()
    fake_st.selectbox_values["_publisher_role"] = "viewer"
    fake_st.button_presses = {"publisher_publish_btn"}
    _run_publisher_wizard(fake_st, store)
    # Warning about authorization should appear
    assert any(
        "not authorised" in msg.lower() or "not authorized" in msg.lower()
        for msg in fake_st.warning_calls
    )


def test_publisher_wizard_authorized_publish_succeeds(tmp_path: Path) -> None:
    """Manager role with all checks passed can publish."""
    store = _make_committed_store(tmp_path)
    history = store.get_history("STUDY-01")
    commit_id_display = f"1.0.0 — {history[0]['commit_id'][:12]} by alice ({history[0]['timestamp'][:19]})"

    fake_st = _FakeStreamlit()
    fake_st.selectbox_values["_publisher_role"] = "manager"
    fake_st.text_input_values["_publisher_user"] = "bob"
    fake_st.selectbox_values["publisher_commit_selector"] = commit_id_display
    fake_st.button_presses = {"publisher_publish_btn"}

    _run_publisher_wizard(fake_st, store)

    # A new publish commit should have been recorded
    history_after = store.get_history("STUDY-01")
    assert len(history_after) == 2
    assert "Published to production" in history_after[-1]["description"]


def test_publisher_wizard_reviewer_blocked(tmp_path: Path) -> None:
    """Reviewer role is also blocked from publishing."""
    store = _make_committed_store(tmp_path)
    fake_st = _FakeStreamlit()
    fake_st.selectbox_values["_publisher_role"] = "reviewer"
    fake_st.button_presses = {"publisher_publish_btn"}
    _run_publisher_wizard(fake_st, store)
    assert any(
        "not authorised" in msg.lower() or "not authorized" in msg.lower()
        for msg in fake_st.warning_calls
    )


def test_publisher_wizard_admin_can_publish(tmp_path: Path) -> None:
    """Admin role can also publish."""
    store = _make_committed_store(tmp_path)
    history = store.get_history("STUDY-01")
    commit_id_display = f"1.0.0 — {history[0]['commit_id'][:12]} by alice ({history[0]['timestamp'][:19]})"

    fake_st = _FakeStreamlit()
    fake_st.selectbox_values["_publisher_role"] = "admin"
    fake_st.text_input_values["_publisher_user"] = "carol"
    fake_st.selectbox_values["publisher_commit_selector"] = commit_id_display
    fake_st.button_presses = {"publisher_publish_btn"}

    _run_publisher_wizard(fake_st, store)

    history_after = store.get_history("STUDY-01")
    assert len(history_after) == 2


def test_publisher_wizard_no_username_blocked(tmp_path: Path) -> None:
    """Publish is blocked when no username is entered."""
    store = _make_committed_store(tmp_path)
    fake_st = _FakeStreamlit()
    fake_st.selectbox_values["_publisher_role"] = "manager"
    # No username set → defaults to empty string
    fake_st.button_presses = {"publisher_publish_btn"}
    _run_publisher_wizard(fake_st, store)
    # Should warn about missing username
    assert any("username" in msg.lower() for msg in fake_st.warning_calls)
