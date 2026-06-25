"""Tests for the plugin contract: PluginProtocol, WorkflowsNamespaceProtocol, PluginLoadError."""

from __future__ import annotations

from importlib.metadata import EntryPoint
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from imednet.errors import PluginLoadError
from imednet.plugins import PluginProtocol, WorkflowsNamespaceProtocol
from imednet.sdk import _BaseSDK

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _ValidNamespace:
    """A minimal object satisfying WorkflowsNamespaceProtocol."""

    data_extraction: Any = None
    query_management: Any = None
    record_mapper: Any = None
    record_update: Any = None
    subject_data: Any = None


def _valid_factory(sdk_instance: Any) -> _ValidNamespace:  # noqa: ANN401
    """Test the valid factory functionality."""
    return _ValidNamespace()


# ---------------------------------------------------------------------------
# WorkflowsNamespaceProtocol runtime check
# ---------------------------------------------------------------------------


def test_valid_namespace_satisfies_protocol() -> None:
    """Test the test valid namespace satisfies protocol functionality."""
    assert isinstance(_ValidNamespace(), WorkflowsNamespaceProtocol)


def test_object_missing_attributes_does_not_satisfy_namespace_protocol() -> None:
    """Test the test object missing attributes does not satisfy namespace protocol functionality."""

    class _Incomplete:
        """Test suite for _Incomplete."""

        data_extraction: Any = None
        # missing: query_management, record_mapper, record_update, subject_data

    assert not isinstance(_Incomplete(), WorkflowsNamespaceProtocol)


# ---------------------------------------------------------------------------
# PluginProtocol runtime check
# ---------------------------------------------------------------------------


def test_callable_factory_satisfies_plugin_protocol() -> None:
    """Test the test callable factory satisfies plugin protocol functionality."""
    assert isinstance(_valid_factory, PluginProtocol)


def test_non_callable_does_not_satisfy_plugin_protocol() -> None:
    """Test the test non callable does not satisfy plugin protocol functionality."""
    assert not isinstance("not-a-callable", PluginProtocol)


# ---------------------------------------------------------------------------
# PluginLoadError is a subclass of ImednetError
# ---------------------------------------------------------------------------


def test_plugin_load_error_is_imednet_error() -> None:
    """Test the test plugin load error is imednet error functionality."""
    from imednet.errors import ImednetError

    err = PluginLoadError("boom")
    assert isinstance(err, ImednetError)
    assert str(err) == "boom"


# ---------------------------------------------------------------------------
# _BaseSDK._get_workflow_entry_point
# ---------------------------------------------------------------------------


def _make_sdk() -> _BaseSDK:
    """Return a _BaseSDK instance without triggering full ImednetSDK init."""
    sdk = object.__new__(_BaseSDK)
    return sdk


def test_get_workflow_entry_point_returns_none_when_no_plugins_installed() -> None:
    """Test the test get workflow entry point returns none when no plugins installed functionality."""
    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[]):
        result = sdk._get_workflow_entry_point()
    assert result is None


def test_get_workflow_entry_point_raises_plugin_load_error_on_multiple_plugins() -> None:
    """Test the test get workflow entry point raises plugin load error on multiple plugins functionality."""
    ep1 = MagicMock(spec=EntryPoint)
    ep1.value = "plugin_a.ns:factory"
    ep2 = MagicMock(spec=EntryPoint)
    ep2.value = "plugin_b.ns:factory"

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep1, ep2]):
        with pytest.raises(PluginLoadError, match="Multiple 'workflows' plugins"):
            sdk._get_workflow_entry_point()


def test_get_workflow_entry_point_returns_single_entry_point() -> None:
    """Test the test get workflow entry point returns single entry point functionality."""
    ep = MagicMock(spec=EntryPoint)
    ep.value = "myplugin.ns:factory"

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep]):
        result = sdk._get_workflow_entry_point()
    assert result is ep


# ---------------------------------------------------------------------------
# _BaseSDK._init_workflows — plugin not installed
# ---------------------------------------------------------------------------


def test_init_workflows_returns_missing_workflows_when_no_plugin() -> None:
    """Test the test init workflows returns missing workflows when no plugin functionality."""
    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[]):
        ns = sdk._init_workflows()

    # Accessing any attribute should raise ImportError (not PluginLoadError)
    with pytest.raises(ImportError, match="imednet-workflows"):
        _ = ns.data_extraction  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# _BaseSDK._init_workflows — plugin installed but broken import
# ---------------------------------------------------------------------------


def test_init_workflows_raises_plugin_load_error_on_broken_entry_point() -> None:
    """Test the test init workflows raises plugin load error on broken entry point functionality."""
    ep = MagicMock(spec=EntryPoint)
    ep.value = "broken.module:factory"
    ep.load.side_effect = ModuleNotFoundError("No module named 'broken'")

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep]):
        with pytest.raises(PluginLoadError, match="Failed to load workflows plugin"):
            sdk._init_workflows()


# ---------------------------------------------------------------------------
# _BaseSDK._init_workflows — plugin loaded but not callable
# ---------------------------------------------------------------------------


def test_init_workflows_raises_plugin_load_error_when_entry_point_not_callable() -> None:
    """Test the test init workflows raises plugin load error when entry point not callable functionality."""
    ep = MagicMock(spec=EntryPoint)
    ep.value = "myplugin.ns:NOT_A_CALLABLE"
    ep.load.return_value = "I am a string, not a callable"  # type: ignore[assignment]

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep]):
        with pytest.raises(PluginLoadError, match="must be a callable"):
            sdk._init_workflows()


# ---------------------------------------------------------------------------
# _BaseSDK._init_workflows — plugin installed and valid
# ---------------------------------------------------------------------------


def test_init_workflows_returns_namespace_from_valid_plugin() -> None:
    """Test the test init workflows returns namespace from valid plugin functionality."""
    ep = MagicMock(spec=EntryPoint)
    ep.value = "myplugin.ns:factory"
    ep.load.return_value = _valid_factory

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep]):
        ns = sdk._init_workflows()

    assert isinstance(ns, _ValidNamespace)


# ---------------------------------------------------------------------------
# _BaseSDK._init_workflows — plugin factory raises TypeError
# ---------------------------------------------------------------------------


def test_init_workflows_raises_plugin_load_error_when_factory_raises_type_error() -> None:
    """Test the test init workflows raises plugin load error when factory raises type error functionality."""

    def _bad_factory(*args: Any, **kwargs: Any) -> None:
        """Test the bad factory functionality."""
        raise TypeError("unexpected argument")

    ep = MagicMock(spec=EntryPoint)
    ep.value = "myplugin.ns:bad_factory"
    ep.load.return_value = _bad_factory

    sdk = _make_sdk()
    with patch("imednet.sdk.entry_points", return_value=[ep]):
        with pytest.raises(PluginLoadError, match="Failed to instantiate workflows"):
            sdk._init_workflows()
