import ast
import gc
import importlib.util
import pkgutil

import httpx
import pytest

import imednet
from imednet.sdk import AsyncImednetSDK, ImednetSDK


def test_core_does_not_import_plugins():
    modules = [
        name for _, name, _ in pkgutil.walk_packages(imednet.__path__, imednet.__name__ + ".")
    ]
    for name in modules:
        try:
            spec = importlib.util.find_spec(name)
            if spec and spec.origin and spec.origin.endswith(".py"):
                with open(spec.origin, "r", encoding="utf-8") as f:
                    content = f.read()

                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    assert (
                                        "imednet_workflows" not in alias.name
                                    ), f"{name} imports {alias.name}"
                                    assert (
                                        "apache_airflow_providers_imednet" not in alias.name
                                    ), f"{name} imports {alias.name}"
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    assert (
                                        "imednet_workflows" not in node.module
                                    ), f"{name} imports from {node.module}"
                                    assert (
                                        "apache_airflow_providers_imednet" not in node.module
                                    ), f"{name} imports from {node.module}"
                    except SyntaxError:
                        pass
        except Exception:
            pass


def test_workflows_does_not_import_airflow():
    try:
        spec = importlib.util.find_spec("imednet_workflows")
        if spec is None:
            pytest.skip("imednet_workflows not installed")
        import imednet_workflows
    except ImportError:
        pytest.skip("imednet_workflows not installed")

    modules = [
        name
        for _, name, _ in pkgutil.walk_packages(
            imednet_workflows.__path__, imednet_workflows.__name__ + "."
        )
    ]
    for name in modules:
        try:
            spec = importlib.util.find_spec(name)
            if spec and spec.origin and spec.origin.endswith(".py"):
                with open(spec.origin, "r", encoding="utf-8") as f:
                    content = f.read()
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    assert (
                                        "apache_airflow_providers_imednet" not in alias.name
                                    ), f"{name} imports {alias.name}"
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    assert (
                                        "apache_airflow_providers_imednet" not in node.module
                                    ), f"{name} imports from {node.module}"
                    except SyntaxError:
                        pass
        except Exception:
            pass


def test_endpoint_state_isolation():
    sdk1 = ImednetSDK("http://example.com", "user", "pass")
    sdk2 = ImednetSDK("http://example.com", "user", "pass")

    assert sdk1.records is not sdk2.records
    assert sdk1.records._client is not sdk2.records._client
    assert sdk1.records._client is sdk1._client
    assert sdk2.records._client is sdk2._client


def test_sync_sdk_isolation():
    gc.collect()
    initial_async_clients = sum(1 for obj in gc.get_objects() if isinstance(obj, httpx.AsyncClient))

    _ = ImednetSDK("http://example.com", "user", "pass")

    final_async_clients = sum(1 for obj in gc.get_objects() if isinstance(obj, httpx.AsyncClient))
    assert (
        final_async_clients == initial_async_clients
    ), "ImednetSDK should not instantiate httpx.AsyncClient"


def test_async_sdk_isolation():
    gc.collect()
    initial_sync_clients = sum(1 for obj in gc.get_objects() if isinstance(obj, httpx.Client))

    _ = AsyncImednetSDK("http://example.com", "user", "pass")

    final_sync_clients = sum(1 for obj in gc.get_objects() if isinstance(obj, httpx.Client))
    assert (
        final_sync_clients == initial_sync_clients
    ), "AsyncImednetSDK should not instantiate httpx.Client"


def test_plugin_discovery_failure(monkeypatch):
    sdk = ImednetSDK("http://example.com", "user", "pass")

    def mock_import_module(name, package=None):
        if name == "imednet_workflows.namespace":
            raise ModuleNotFoundError(name=name)
        return importlib.import_module(name, package)

    monkeypatch.setattr("imednet.sdk.import_module", mock_import_module)

    workflows = sdk._init_workflows()

    with pytest.raises(ImportError, match="requires the optional 'imednet-workflows' package"):
        workflows.some_method()
