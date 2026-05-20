import ast
import importlib
from pathlib import Path

import pytest
from httpx import AsyncClient, Client

import imednet
from imednet.sdk import AsyncImednetSDK, ImednetSDK

try:
    import imednet_workflows
except ImportError:
    imednet_workflows = None


def get_all_python_files(package_path: Path) -> list[Path]:
    return list(package_path.rglob("*.py"))


def get_imports_from_file(file_path: Path) -> set[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        # We want SyntaxError to be raised if a file cannot be parsed, rather than silently ignored.
        tree = ast.parse(f.read(), filename=str(file_path))

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.add(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_core_does_not_import_cli():
    """Ensure no file outside of imednet/cli/ imports the cli module."""
    core_dir = Path(imednet.__file__).parent
    cli_dir = core_dir / "cli"

    for file in get_all_python_files(core_dir):
        # Skip CLI directory itself and its subdirectories
        if cli_dir in file.parents or file.parent == cli_dir:
            continue

        imports = get_imports_from_file(file)
        for imp in imports:
            assert not imp.startswith(
                "imednet.cli"
            ), f"Architectural violation: {file} imports '{imp}' from the CLI layer"


def test_core_does_not_import_workflows():
    core_dir = Path(imednet.__file__).parent
    files = get_all_python_files(core_dir)
    assert len(files) > 0, f"No files found to test in {core_dir}"

    for file in files:
        imports = get_imports_from_file(file)
        for imp in imports:
            assert not imp.startswith("imednet_workflows"), f"File {file} has hard import of {imp}"
            assert not imp.startswith(
                "apache_airflow_providers_imednet"
            ), f"File {file} has hard import of {imp}"


def test_workflows_does_not_import_providers():
    if imednet_workflows is None:
        pytest.skip("imednet_workflows not installed")

    workflows_dir = Path(imednet_workflows.__file__).parent
    files = get_all_python_files(workflows_dir)
    assert len(files) > 0, f"No files found to test in {workflows_dir}"

    for file in files:
        imports = get_imports_from_file(file)
        for imp in imports:
            assert not imp.startswith(
                "apache_airflow_providers_imednet"
            ), f"File {file} has hard import of {imp}"


def test_endpoint_no_shared_mutable_state():
    sdk = ImednetSDK(api_key="1", security_key="2", base_url="http://x")

    assert sdk.records is not sdk.forms

    if hasattr(sdk.records, "_cache"):
        assert sdk.records._cache is not getattr(sdk.forms, "_cache", None)

    # Let's instantiate another SDK and ensure endpoint instances are distinct
    sdk2 = ImednetSDK(api_key="1", security_key="2", base_url="http://x")
    assert sdk.records is not sdk2.records
    assert sdk._client is not sdk2._client


def test_sync_sdk_no_async_client(monkeypatch):
    instantiated = False
    original_init = AsyncClient.__init__

    def mock_init(self, *args, **kwargs):
        nonlocal instantiated
        instantiated = True
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(AsyncClient, "__init__", mock_init)

    with ImednetSDK(api_key="1", security_key="2", base_url="http://x"):
        pass
    assert not instantiated, "ImednetSDK should not instantiate AsyncClient"


def test_async_sdk_no_sync_client(monkeypatch):
    instantiated = False
    original_init = Client.__init__

    def mock_init(self, *args, **kwargs):
        nonlocal instantiated
        instantiated = True
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(Client, "__init__", mock_init)

    AsyncImednetSDK(api_key="1", security_key="2", base_url="http://x")
    assert not instantiated, "AsyncImednetSDK should not instantiate Client"


def test_plugin_discovery_failure(monkeypatch):
    original_import = importlib.import_module

    def mock_import(name, package=None):
        if name == "imednet_workflows.namespace":
            raise ModuleNotFoundError(name=name)
        return original_import(name, package)

    # We patch import_module in imednet.sdk because it imports it directly:
    # `from importlib import import_module`
    monkeypatch.setattr("imednet.sdk.import_module", mock_import)

    sdk = ImednetSDK(api_key="1", security_key="2", base_url="http://x")
    with pytest.raises(ImportError, match="requires the optional 'imednet-workflows' package"):
        sdk.workflows.some_workflow
