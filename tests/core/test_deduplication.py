"""
Unit tests for deduplication logic using Redis hash caching.

Uses mocking to simulate Redis responses and isolate logic under test.
"""

import pytest
from unittest.mock import patch
from app.core.deduplication import is_already_processed

# Sample input for testing
TEXT_INPUT = "This is a sample input for deduplication."


@pytest.mark.redis
@patch("app.core.deduplication.set_cache")
@patch("app.core.deduplication.get_cache")
def test_text_already_processed(mock_get_cache, mock_set_cache):
    """
    Test that known hash is detected as already processed.

    Mocks Redis to simulate a cache hit.
    """
    mock_get_cache.return_value = "1"  # Simulate existing cache entry

    result = is_already_processed(TEXT_INPUT)

    assert result is True
    mock_get_cache.assert_called_once()
    mock_set_cache.assert_not_called()


@pytest.mark.redis
@patch("app.core.deduplication.set_cache")
@patch("app.core.deduplication.get_cache")
def test_text_not_yet_processed(mock_get_cache, mock_set_cache):
    """
    Test that new text is marked as processed when not found in cache.

    Simulates first-time input.
    """
    mock_get_cache.return_value = None  # No cache hit
    mock_set_cache.return_value = True  # Assume setting works

    result = is_already_processed(TEXT_INPUT)

    assert result is False  # Return False to indicate it's *not* already processed
    mock_get_cache.assert_called_once()
    mock_set_cache.assert_called_once()


@pytest.mark.redis
@patch("app.core.deduplication.set_cache")
@patch("app.core.deduplication.get_cache")
def test_invalid_text_input(mock_get_cache, mock_set_cache):
    """
    Test that invalid input (e.g., None) is handled gracefully.
    """
    invalid_input = None
    result = is_already_processed(invalid_input)

    assert result is False
    mock_get_cache.assert_not_called()
    mock_set_cache.assert_not_called()
