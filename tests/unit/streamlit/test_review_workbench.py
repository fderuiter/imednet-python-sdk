from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

from imednet.models.triage import TriageAnnotation, TriageHistoryEntry, TriageItem, TriageStatus

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKBENCH_PATH = (
    REPO_ROOT
    / "packages"
    / "plugins-streamlit"
    / "src"
    / "imednet_streamlit"
    / "pages"
    / "review_workbench.py"
)
DRAWER_PATH = (
    REPO_ROOT
    / "packages"
    / "plugins-streamlit"
    / "src"
    / "imednet_streamlit"
    / "components"
    / "triage_drawer.py"
)


class _FakeContextManager:
    def __enter__(self) -> "_FakeContextManager":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _FakeStreamlit:
    def __init__(self) -> None:
        self.session_state: dict[str, Any] = {}
        self.metrics: dict[str, Any] = {}
        self.frames: list[Any] = []
        self.multiselect_values: dict[str, list[str]] = {}
        self.text_values: dict[str, str] = {}
        self.selectbox_values: dict[str, str] = {}

    def title(self, value: str) -> None:
        pass

    def markdown(self, value: str, **kwargs: Any) -> None:
        pass

    def info(self, value: str) -> None:
        pass

    def columns(self, spec: int | list[Any]) -> list[_FakeContextManager]:
        count = spec if isinstance(spec, int) else len(spec)
        return [_FakeContextManager() for _ in range(count)]

    def metric(self, label: str, value: Any, **kwargs: Any) -> None:
        self.metrics[label] = value

    def multiselect(self, label: str, options: list[str], **kwargs: Any) -> list[str]:
        return self.multiselect_values.get(label, list(kwargs.get("default", [])))

    def text_input(self, label: str, **kwargs: Any) -> str:
        return self.text_values.get(label, "")

    def dataframe(self, df: Any, **kwargs: Any) -> None:
        self.frames.append(df)

    def selectbox(self, label: str, options: list[str], index: int = 0, **kwargs: Any) -> str:
        return self.selectbox_values.get(label, options[index])

    def subheader(self, value: str) -> None:
        pass

    def caption(self, value: str) -> None:
        pass

    def write(self, value: str) -> None:
        pass

    def button(self, label: str, **kwargs: Any) -> bool:
        return False

    def text_area(self, label: str, **kwargs: Any) -> str:
        return ""

    def success(self, value: str) -> None:
        pass

    def warning(self, value: str) -> None:
        pass


def _sample_items() -> list[TriageItem]:
    old_ts = datetime.now(timezone.utc) - timedelta(hours=96)
    recent_ts = datetime.now(timezone.utc) - timedelta(hours=2)
    return [
        TriageItem(
            item_id="AE-1",
            study_key="STUDY-X",
            status=TriageStatus.NEW,
            assignee="alice",
            severity="critical",
            annotations=[],
            history=[
                TriageHistoryEntry(
                    transition_id="h1",
                    from_status=TriageStatus.NEW,
                    to_status=TriageStatus.NEW,
                    user_id="alice",
                    comment="created",
                    timestamp=old_ts,
                )
            ],
        ),
        TriageItem(
            item_id="PD-2",
            study_key="STUDY-X",
            status=TriageStatus.RESOLVED,
            assignee="bob",
            severity="warning",
            annotations=[
                TriageAnnotation(
                    annotation_id="a1",
                    user_id="bob",
                    comment="resolved",
                    timestamp=recent_ts,
                )
            ],
            history=[],
        ),
    ]


def test_review_workbench_renders_kpis_and_filters_queue() -> None:
    fake_st = _FakeStreamlit()
    fake_st.multiselect_values = {
        "Severity": ["Critical/Severe"],
        "Category": ["Adverse Event", "Deviation", "Deficiency", "Other"],
        "Assignee": ["alice", "bob"],
    }

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "title",
        "markdown",
        "info",
        "columns",
        "metric",
        "multiselect",
        "text_input",
        "dataframe",
        "selectbox",
        "subheader",
        "caption",
        "write",
        "button",
        "text_area",
        "success",
        "warning",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))

    fake_auth_module = ModuleType("imednet_streamlit.auth")
    fake_auth_module.get_study_key = lambda: "STUDY-X"  # type: ignore[attr-defined]

    fake_drawer_module = ModuleType("imednet_streamlit.components.triage_drawer")

    fake_components_package = ModuleType("imednet_streamlit.components")
    drawer_mock = MagicMock()
    fake_drawer_module.render_triage_drawer = drawer_mock  # type: ignore[attr-defined]
    fake_components_package.triage_drawer = fake_drawer_module  # type: ignore[attr-defined]

    fake_store_module = ModuleType("imednet_workflows.triage_store")
    fake_store_cls = MagicMock()
    fake_store_instance = MagicMock()
    fake_store_instance.get_queue.return_value = _sample_items()
    fake_store_cls.return_value = fake_store_instance
    fake_store_module.TriageStore = fake_store_cls  # type: ignore[attr-defined]

    saved = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_streamlit.auth",
            "imednet_streamlit.components",
            "imednet_streamlit.components.triage_drawer",
            "imednet_workflows.triage_store",
        )
    }

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_streamlit.auth"] = fake_auth_module
        sys.modules["imednet_streamlit.components"] = fake_components_package
        sys.modules["imednet_streamlit.components.triage_drawer"] = fake_drawer_module
        sys.modules["imednet_workflows.triage_store"] = fake_store_module

        module_name = "imednet_streamlit.pages.review_workbench"
        spec = importlib.util.spec_from_file_location(module_name, WORKBENCH_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value

    assert fake_st.metrics["Open Queue"] == 1
    assert fake_st.metrics["SLA >72h"] == 1
    assert fake_st.metrics["Resolved"] == 1
    filtered_df = fake_st.frames[0]
    assert filtered_df["item_id"].tolist() == ["AE-1"]
    assert drawer_mock.called


def test_triage_drawer_submits_assignment_annotation_and_status() -> None:
    fake_st = _FakeStreamlit()

    def _always_true(label: str, **kwargs: Any) -> bool:
        return True

    fake_st.button = _always_true  # type: ignore[assignment]
    fake_st.text_area = lambda label, **kwargs: "follow-up"  # type: ignore[assignment]
    fake_st.selectbox_values = {
        "Change Assignee": "alice",
        "Triage Capture": TriageStatus.UNDER_REVIEW.value,
    }

    fake_streamlit_module = ModuleType("streamlit")
    fake_streamlit_module.session_state = fake_st.session_state  # type: ignore[attr-defined]
    for attr in (
        "subheader",
        "caption",
        "write",
        "selectbox",
        "button",
        "text_area",
        "success",
        "warning",
    ):
        setattr(fake_streamlit_module, attr, getattr(fake_st, attr))

    saved = {
        key: sys.modules.get(key)
        for key in (
            "streamlit",
            "imednet_workflows.triage_store",
        )
    }

    fake_store_module = ModuleType("imednet_workflows.triage_store")
    fake_store_module.TriageStore = object  # type: ignore[attr-defined]

    try:
        sys.modules["streamlit"] = fake_streamlit_module
        sys.modules["imednet_workflows.triage_store"] = fake_store_module

        module_name = "imednet_streamlit.components.triage_drawer"
        spec = importlib.util.spec_from_file_location(module_name, DRAWER_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        item = _sample_items()[0]
        store = MagicMock()
        module.render_triage_drawer(
            store=store,
            item=item,
            assignee_options=["alice", "bob"],
            current_user="reviewer",
        )
    finally:
        for key, value in saved.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value

    store.assign_item.assert_called_once_with("AE-1", "alice")
    store.add_annotation.assert_called_once_with("AE-1", "reviewer", "follow-up")
    store.update_status.assert_called_once_with(
        "AE-1", TriageStatus.UNDER_REVIEW, "reviewer", "follow-up"
    )
