"""
Defines the API routes for receiving and validating text input.

Routes:
- POST /text: Accepts validated text input and sends to Kafka.
"""

from fastapi import APIRouter, HTTPException
from app.models.input import TextRequest
from app.core.logging_config import logger
import app.core.kafka_producer as kafka_producer

router = APIRouter()


@router.post("/text")
def receive_text(payload: TextRequest):
    """
    Receives a text payload from the client and sends it to Kafka.

    Args:
        payload (TextRequest): The incoming text message as a Pydantic model.

    Returns:
        dict: A confirmation message indicating the result.

    Raises:
        HTTPException: 400 - invalid input, 500 - Kafka failure.
    """
    if not payload.text or not payload.text.strip():
        logger.warning("Empty or missing 'text' field in request.")
        raise HTTPException(status_code=400, detail="The 'text' field is required and cannot be empty.")

    success = kafka_producer.send_text_to_kafka(payload.model_dump())

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message to Kafka")

    logger.info("✅ Text accepted and sent to Kafka.")
    return {"status": "Message sent to Kafka"}
