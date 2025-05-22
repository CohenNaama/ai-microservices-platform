"""
API tests for /text route using FastAPI TestClient.

Covers success, validation errors, and simulated Kafka failures.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import core.kafka_producer as kafka_producer

client = TestClient(app)


@pytest.mark.api
@patch("app.api.routes.kafka_producer.send_text_to_kafka")
def test_send_valid_text(mock_send_kafka):
    """
    Test sending a valid text payload to /text endpoint.

    Should return 200 OK.
    """
    mock_send_kafka.return_value = True

    response = client.post("/text", json={"text": "Hello world!"})
    assert response.status_code == 200
    assert response.json() == {"status": "Message sent to Kafka"}


@pytest.mark.api
@patch("app.api.routes.kafka_producer.send_text_to_kafka")
def test_send_empty_text(mock_send_kafka):
    """
    Test sending an empty text string.

    Should return 400 Bad Request.
    """
    response = client.post("/text", json={"text": "   "})
    assert response.status_code == 400
    assert "text" in response.json()["detail"]
    mock_send_kafka.assert_not_called()


@pytest.mark.api
@patch("app.api.routes.kafka_producer.send_text_to_kafka")

# @patch("app.api.routes.send_text_to_kafka")
def test_kafka_failure_returns_500(mock_send_kafka):
    """
    Simulate Kafka send failure.

    Should return 500 Internal Server Error.
    """
    mock_send_kafka.return_value = False

    response = client.post("/text", json={"text": "Test message"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to send message to Kafka"


@pytest.mark.api
def test_missing_text_field_schema_error():
    """
    Send payload missing 'text' field.

    Should trigger 422 validation error.
    """
    response = client.post("/text", json={})
    assert response.status_code == 422
    assert "detail" in response.json()
