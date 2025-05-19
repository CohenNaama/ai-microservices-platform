"""
Unit tests for Kafka Producer logic.

Validates message handling, schema enforcement, and Kafka error simulation using mocking.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.core.kafka_producer import send_text_to_kafka
from kafka.errors import KafkaError


@pytest.mark.kafka
@patch("app.core.kafka_producer.producer")
def test_send_valid_text(mock_producer):
    """
    Test sending a valid message to Kafka.

    Simulates successful send + flush.
    """
    # Arrange
    mock_producer.send.return_value = MagicMock()
    mock_producer.flush.return_value = None

    data = {"text": "Hello Kafka"}

    # Act
    result = send_text_to_kafka(data)

    # Assert
    assert result is True
    mock_producer.send.assert_called_once()
    mock_producer.flush.assert_called_once()


@pytest.mark.kafka
@patch("app.core.kafka_producer.producer")
def test_missing_text_field(mock_producer):
    """
    Test sending a message without the 'text' field.

    Expected to fail validation.
    """
    data = {"message": "no text key"}

    result = send_text_to_kafka(data)

    assert result is False
    mock_producer.send.assert_not_called()


@pytest.mark.kafka
@patch("app.core.kafka_producer.producer")
def test_invalid_data_type(mock_producer):
    """
    Test sending invalid data (non-dict).

    Should log error and return False.
    """
    result = send_text_to_kafka("this is not a dict")

    assert result is False
    mock_producer.send.assert_not_called()


@pytest.mark.kafka
@patch("app.core.kafka_producer.producer")
def test_kafka_send_failure(mock_producer):
    """
    Test Kafka producer failure during send.

    Mocks KafkaError to simulate failure path.
    """
    mock_producer.send.side_effect = KafkaError("Kafka send error")

    data = {"text": "this will fail"}

    result = send_text_to_kafka(data)

    assert result is False
    mock_producer.send.assert_called_once()
