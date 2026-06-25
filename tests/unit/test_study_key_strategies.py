"""Test Study Key Strategies module."""

from imednet.core.endpoint.strategies import (
    KeepStudyKeyStrategy,
    OptionalStudyKeyStrategy,
    PopStudyKeyStrategy,
)


class TestKeepStudyKeyStrategy:
    """Test suite for TestKeepStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test the test process with valid key functionality."""
        strategy = KeepStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_missing_key(self):
        """Test the test process missing key functionality."""
        strategy = KeepStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters


class TestPopStudyKeyStrategy:
    """Test suite for TestPopStudyKeyStrategy."""

    def test_process_with_valid_key(self):
        """Test the test process with valid key functionality."""
        strategy = PopStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == {"other": "val"}

    def test_process_missing_key(self):
        """Test the test process missing key functionality."""
        strategy = PopStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == {"other": "val"}


class TestOptionalStudyKeyStrategy:
    """Test suite for TestOptionalStudyKeyStrategy."""

    def test_process_with_key(self):
        """Test the test process with key functionality."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"studyKey": "study-123", "other": "val"}
        key, new_filters = strategy.process(filters)
        assert key == "study-123"
        assert new_filters == filters

    def test_process_without_key(self):
        """Test the test process without key functionality."""
        strategy = OptionalStudyKeyStrategy()
        filters = {"other": "val"}
        key, new_filters = strategy.process(filters)
        assert key is None
        assert new_filters == filters
