from unittest.mock import Mock

import scripts.post_smoke_record as smoke


def test_submit_record_uses_configured_timeout() -> None:
    sdk = Mock()
    sdk.records.create.return_value = Mock(batch_id="B1")
    sdk.poll_job.return_value = Mock(state="COMPLETED", batch_id="B1")

    batch_id = smoke.submit_record(sdk, "ST", {"data": {}})

    assert batch_id == "B1"
    sdk.poll_job.assert_called_once_with("ST", "B1", interval=1, timeout=smoke.POLL_TIMEOUT)
