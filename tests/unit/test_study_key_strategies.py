"""Unit tests for study key strategies."""

from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
)


class TestKeepStudyKeyStrategy:
    """Test suite for KeepStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test that process with valid key."""
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_missing_key(self):
        """Test that process missing key."""
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters


class TestPopStudyKeyStrategy:
    """Test suite for PopStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test that process with valid key."""
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == {"other": "val"}

    def test_process_missing_key(self):
        """Test that process missing key."""
        strategy = PopStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == {"other": "val"}


class TestOptionalStudyKeyStrategy:
    """Test suite for OptionalStudyKeyStrategy."""

    def test_process_with_key(self):
        """Test that process with key."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_without_key(self):
        """Test that process without key."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters
