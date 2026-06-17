from unittest.mock import MagicMock

import pandas as pd
import pytest

from imednet_streamlit.components.tables import apply_enrichment_to_df


def test_apply_enrichment_empty_df():
    df = pd.DataFrame()
    result = apply_enrichment_to_df(df)
    assert result.empty


def test_apply_enrichment_sensitive_masking(monkeypatch):
    import imednet.utils.security

    mock_registry = MagicMock()
    mock_registry.is_sensitive.side_effect = lambda col: col == "secret"
    monkeypatch.setattr(imednet.utils.security, "global_sensitivity_registry", mock_registry)

    df = pd.DataFrame({"normal": [1], "secret": ["hidden"]})

    # Mock get_study_key to raise RuntimeError
    import imednet_streamlit.auth

    monkeypatch.setattr(
        imednet_streamlit.auth, "get_study_key", MagicMock(side_effect=RuntimeError)
    )

    result = apply_enrichment_to_df(df)
    assert result["normal"].iloc[0] == 1
    assert result["secret"].iloc[0] == "***MASKED***"


def test_apply_enrichment_pipeline(monkeypatch):
    import imednet.utils.security

    mock_registry = MagicMock()
    mock_registry.is_sensitive.return_value = False
    monkeypatch.setattr(imednet.utils.security, "global_sensitivity_registry", mock_registry)

    import imednet_streamlit.auth

    monkeypatch.setattr(imednet_streamlit.auth, "get_study_key", MagicMock(return_value="study1"))

    import imednet_workflows.config_version_control

    mock_store = MagicMock()
    mock_store_instance = mock_store.return_value
    mock_store_instance.get_history.return_value = [{"commit_id": "commit1"}]
    mock_store_instance.rollback_config.return_value = {"config": "val"}
    monkeypatch.setattr(imednet_workflows.config_version_control, "ConfigVersionStore", mock_store)

    import imednet.integrations.enrichment

    mock_pipeline_cls = MagicMock()
    mock_pipeline_instance = mock_pipeline_cls.return_value
    mock_pipeline_instance.process.return_value = [{"normal": 2}]
    monkeypatch.setattr(imednet.integrations.enrichment, "EnrichmentPipeline", mock_pipeline_cls)

    df = pd.DataFrame({"normal": [1]})
    result = apply_enrichment_to_df(df)

    assert result["normal"].iloc[0] == 2
    mock_store_instance.get_history.assert_called_with("study1")
    mock_store_instance.rollback_config.assert_called_with("study1", "commit1")


def test_apply_enrichment_pipeline_exception(monkeypatch):
    import imednet.utils.security

    mock_registry = MagicMock()
    mock_registry.is_sensitive.return_value = False
    monkeypatch.setattr(imednet.utils.security, "global_sensitivity_registry", mock_registry)

    import imednet_streamlit.auth

    monkeypatch.setattr(imednet_streamlit.auth, "get_study_key", MagicMock(return_value="study1"))

    import imednet_workflows.config_version_control

    mock_store = MagicMock()
    mock_store_instance = mock_store.return_value
    mock_store_instance.get_history.side_effect = Exception("error")
    monkeypatch.setattr(imednet_workflows.config_version_control, "ConfigVersionStore", mock_store)

    df = pd.DataFrame({"normal": [1]})
    result = apply_enrichment_to_df(df)

    assert result["normal"].iloc[0] == 1
