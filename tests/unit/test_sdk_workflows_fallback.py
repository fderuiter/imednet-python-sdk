import importlib
import sys
from unittest.mock import MagicMock

import pytest

from imednet.sdk import ImednetSDK


def test_missing_workflows_getattr(monkeypatch):
    original_import_module = importlib.import_module

    def fake_import_module(name, package=None):
        if name == "imednet_workflows.namespace":
            raise ModuleNotFoundError(
                "No module named 'imednet_workflows'", name="imednet_workflows"
            )
        return original_import_module(name, package)

    monkeypatch.setattr("imednet.sdk.import_module", fake_import_module)
    monkeypatch.setitem(sys.modules, "imednet.workflows.namespace", None)
    monkeypatch.setitem(sys.modules, "imednet.workflows", None)

    sdk = ImednetSDK(api_key="key", security_key="secret", base_url="https://example.com")

    with pytest.raises(ImportError) as exc:
        _ = sdk.workflows.some_workflow

    assert "Workflow 'some_workflow' requires the optional" in str(exc.value)


def test_imednet_workflows_installed_but_no_workflows_cls(monkeypatch):
    original_import_module = importlib.import_module

    fake_module = MagicMock()
    fake_module.Workflows = None
    del fake_module.Workflows

    def fake_import_module(name, package=None):
        if name == "imednet_workflows.namespace":
            return fake_module
        return original_import_module(name, package)

    monkeypatch.setattr("imednet.sdk.import_module", fake_import_module)

    with pytest.raises(ImportError) as exc:
        ImednetSDK(api_key="key", security_key="secret", base_url="https://example.com")

    assert "module does not export 'Workflows'" in str(exc.value)


def test_imednet_workflows_installed_but_instantiation_fails_with_attribute_error(monkeypatch):
    original_import_module = importlib.import_module

    fake_module = MagicMock()

    def raising_workflows(sdk):
        raise AttributeError("mock error")

    fake_module.Workflows = raising_workflows

    def fake_import_module(name, package=None):
        if name == "imednet_workflows.namespace":
            return fake_module
        return original_import_module(name, package)

    monkeypatch.setattr("imednet.sdk.import_module", fake_import_module)

    with pytest.raises(ImportError) as exc:
        ImednetSDK(api_key="key", security_key="secret", base_url="https://example.com")

    assert "Failed to instantiate Workflows from imednet_workflows.namespace" in str(exc.value)


def test_other_module_not_found_error_is_raised(monkeypatch):
    original_import_module = importlib.import_module

    def fake_import_module(name, package=None):
        if name == "imednet_workflows.namespace":
            raise ModuleNotFoundError(
                "No module named 'some_other_module'", name="some_other_module"
            )
        return original_import_module(name, package)

    monkeypatch.setattr("imednet.sdk.import_module", fake_import_module)

    with pytest.raises(ModuleNotFoundError) as exc:
        ImednetSDK(api_key="key", security_key="secret", base_url="https://example.com")

    assert "some_other_module" in str(exc.value)
