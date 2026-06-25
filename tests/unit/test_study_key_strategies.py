"""Tests for test_study_key_strategies."""

from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
)


class TestKeepStudyKeyStrategy:
    """Test suite for TestKeepStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test test_process_with_valid_key behavior."""
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_missing_key(self):
        """Test test_process_missing_key behavior."""
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters


class TestPopStudyKeyStrategy:
    """Test suite for TestPopStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test test_process_with_valid_key behavior."""
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == {"other": "val"}

    def test_process_missing_key(self):
        """Test test_process_missing_key behavior."""
        strategy = PopStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == {"other": "val"}


class TestOptionalStudyKeyStrategy:
    """Test suite for TestOptionalStudyKeyStrategy."""

    def test_process_with_key(self):
        """Test test_process_with_key behavior."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_without_key(self):
        """Test test_process_without_key behavior."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters
