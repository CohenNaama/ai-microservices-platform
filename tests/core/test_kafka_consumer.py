"""
Unit tests for Kafka consumer's process_message function.

Covers message validation, deduplication logic, and Redis caching using mocking.
"""

import pytest
from unittest.mock import patch

from app.core.kafka_consumer import process_message


@patch("app.core.kafka_consumer.set_cache")
@patch("app.core.kafka_consumer.is_already_processed")
def test_valid_message_processing(mock_dedup, mock_cache):
    """
    Test processing of a valid message that is not duplicated.

    Should call Redis set_cache with expected key/value.
    """
    mock_dedup.return_value = False
    mock_cache.return_value = True

    message = {
        "text": "Hello world!",
        "user_id": "user123"
    }

    result = process_message(message)

    assert result is None  # Function returns None by design
    mock_dedup.assert_called_once()
    mock_cache.assert_called_once()


@patch("app.core.kafka_consumer.set_cache")
@patch("app.core.kafka_consumer.is_already_processed")
def test_duplicate_message_skipped(mock_dedup, mock_cache):
    """
    Test that duplicated messages are skipped and not cached.
    """
    mock_dedup.return_value = True

    message = {
        "text": "Repeated message",
        "user_id": "user123"
    }

    result = process_message(message)

    assert result is None
    mock_dedup.assert_called_once()
    mock_cache.assert_not_called()


@patch("app.core.kafka_consumer.set_cache")
@patch("app.core.kafka_consumer.is_already_processed")
def test_message_missing_text_field(mock_dedup, mock_cache):
    """
    Test that message without 'text' field is rejected.
    """
    message = {
        "user_id": "user123"
    }

    result = process_message(message)

    assert result is None
    mock_dedup.assert_not_called()
    mock_cache.assert_not_called()


@patch("app.core.kafka_consumer.set_cache")
@patch("app.core.kafka_consumer.is_already_processed")
def test_invalid_message_type(mock_dedup, mock_cache):
    """
    Test that message that is not a dictionary is rejected.

    (e.g. string, list, etc.)
    """
    result = process_message("this is not a dict")

    assert result is None
    mock_dedup.assert_not_called()
    mock_cache.assert_not_called()
