"""Tests for contract validation across namespaces and plugins."""

import inspect
from unittest.mock import MagicMock

import pytest

from imednet_sinks.plugin import SinksNamespace
from imednet_workflows.namespace import Workflows


def test_sinks_namespace_contract():
    """Verify that MongoDbSinkConfig is accessible dynamically on SinksNamespace."""
    mock_sdk = MagicMock()
    sinks_ns = SinksNamespace(mock_sdk)
    
    # Should not raise an AttributeError
    try:
        mongo_config = sinks_ns.MongoDbSinkConfig
    except AttributeError as e:
        pytest.fail(f"Failed to access MongoDbSinkConfig: {e}")
    
    assert mongo_config is not None


def test_workflows_namespace_contract():
    """Verify that duckdb_centralizer is instantiated and accessible on Workflows."""
    mock_sdk = MagicMock()
    workflows_ns = Workflows(mock_sdk)
    
    # Should not raise an AttributeError
    try:
        duckdb_workflow = workflows_ns.duckdb_centralizer
    except AttributeError as e:
        pytest.fail(f"Failed to access duckdb_centralizer: {e}")
        
    assert duckdb_workflow is not None


def test_workflow_constructors_contract():
    """Verify that all workflow constructors accept at most one mandatory argument (the SDK client)."""
    mock_sdk = MagicMock()
    workflows_ns = Workflows(mock_sdk)
    
    for attr_name, attr_val in vars(workflows_ns).items():
        if attr_name.startswith("_"):
            continue
        
        cls = attr_val.__class__
        sig = inspect.signature(cls.__init__)
        
        mandatory_params = []
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.default is inspect.Parameter.empty:
                mandatory_params.append(param_name)
                
        assert len(mandatory_params) <= 1, (
            f"Workflow class {cls.__name__} constructor requires more than one mandatory argument: "
            f"{mandatory_params}. It must accept only the SDK client as a mandatory argument."
        )
