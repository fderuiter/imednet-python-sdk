from unittest.mock import Mock

import pytest
import scripts.post_smoke_record as smoke


def test_submit_record_uses_configured_timeout() -> None:
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="COMPLETED", batch_id="B1")

    batch_id = smoke.submit_record(sdk, "ST", {"data": {}}, timeout=123)

    assert batch_id == "B1"
    sdk.poll_job.assert_called_once_with("ST", "B1", interval=1, timeout=123)


def test_submit_record_reports_failure_details() -> None:
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="FAILED", batch_id="B1", result_url="https://x")
    response = Mock(text="Form with formKey of SS not found.")
    response.json.side_effect = ValueError()
    sdk._client.get.return_value = response

    with pytest.raises(RuntimeError, match="FAILED: Form with formKey"):
        smoke.submit_record(sdk, "ST", {"data": {}}, timeout=1)

    sdk._client.get.assert_called_once_with("https://x")
