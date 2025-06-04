"""
Defines the API routes for receiving and validating text input.

Routes:
- POST /text: Accepts validated text input and sends to Kafka.
"""
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from app.models.input import TextRequest
from app.core.logging_config import logger
import app.core.kafka_producer as kafka_producer

router = APIRouter()


@router.post("/text")
def receive_text(payload: TextRequest):
    """
    Receives a text payload from the client, generates a unique text_id, and sends it to Kafka.

    Args:
        payload (TextRequest): The incoming text message, including user_id and text.

    Returns:
        dict: A confirmation message including the generated text_id.

    Raises:
        HTTPException:
            400 - If the 'text' field is empty.
            500 - If sending the message to Kafka fails.
    """
    if not payload.text or not payload.text.strip():
        logger.warning("Empty or missing 'text' field in request.")
        raise HTTPException(status_code=400, detail="The 'text' field is required and cannot be empty.")

    text_id = str(uuid4())

    message = {
        "text_id": text_id,
        "user_id": payload.user_id,
        "text": payload.text
    }

    success = kafka_producer.send_text_to_kafka(message)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message to Kafka")

    logger.info(f"Text accepted with text_id={text_id} and sent to Kafka.")
    return {"status": "Message sent to Kafka", "text_id": text_id}
