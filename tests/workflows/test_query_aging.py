from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from imednet.models.queries import Query, QueryComment
from imednet.workflows.query_aging import QueryAgingWorkflow


class TestQueryAgingWorkflow:
    """Tests for the QueryAgingWorkflow class."""

    @staticmethod
    def _make_query(age_days: int) -> Query:
        dt = datetime.now(timezone.utc) - timedelta(days=age_days)
        comment = QueryComment(sequence=1, closed=False, date=dt)
        return Query(date_created=dt, query_comments=[comment])

    @pytest.fixture
    def mock_sdk(self):
        return MagicMock()

    def test_aging_summary_default_buckets(self, mock_sdk):
        queries = [
            self._make_query(3),
            self._make_query(8),
            self._make_query(15),
            self._make_query(40),
        ]
        mock_qm = MagicMock()
        mock_qm.get_open_queries.return_value = queries
        with patch("imednet.workflows.query_aging.QueryManagementWorkflow", return_value=mock_qm):
            wf = QueryAgingWorkflow(mock_sdk)
            result = wf.aging_summary("STUDY")

        assert result == {"0-7": 1, "8-14": 1, "15-30": 1, ">30": 1}
        mock_qm.get_open_queries.assert_called_once_with("STUDY")

    def test_aging_summary_custom_buckets(self, mock_sdk):
        queries = [
            self._make_query(5),
            self._make_query(12),
            self._make_query(25),
        ]
        mock_qm = MagicMock()
        mock_qm.get_open_queries.return_value = queries
        with patch("imednet.workflows.query_aging.QueryManagementWorkflow", return_value=mock_qm):
            wf = QueryAgingWorkflow(mock_sdk)
            result = wf.aging_summary("STUDY", buckets=[10, 20])

        assert result == {"0-10": 1, "11-20": 1, ">20": 1}
