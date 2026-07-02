import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from imednet_workflows.state_ledger import AirflowStateProvider


@pytest.fixture
def mock_airflow():
    mock_airflow = MagicMock()
    sys.modules['airflow'] = mock_airflow
    sys.modules['airflow.operators.python'] = MagicMock()
    sys.modules['airflow.models.xcom'] = MagicMock()
    sys.modules['airflow.utils.session'] = MagicMock()
    yield mock_airflow
    del sys.modules['airflow']
    del sys.modules['airflow.operators.python']
    del sys.modules['airflow.models.xcom']
    del sys.modules['airflow.utils.session']

def test_airflow_provider_fallback_transaction(mock_airflow):
    provider = AirflowStateProvider()
    
    mock_get_current_context = sys.modules['airflow.operators.python'].get_current_context
    mock_ti = MagicMock()
    mock_get_current_context.return_value = {"ti": mock_ti}
    
    with provider.transaction("study1", "stream1", fallback_timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc)) as tx:
        tx["new_timestamp"] = datetime(2026, 1, 2, tzinfo=timezone.utc)
        tx["records_processed"] = 5
        
    assert mock_ti.xcom_push.called
