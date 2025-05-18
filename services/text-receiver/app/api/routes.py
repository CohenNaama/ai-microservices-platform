from fastapi import APIRouter, HTTPException
from app.models.input import TextRequest
from app.core.kafka_producer import send_text_to_kafka

router = APIRouter()


@router.post("/text")
def receive_text(payload: TextRequest):
    success = send_text_to_kafka(payload.dict())
    print("📨 Sent message:", payload.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send message to Kafka")
    return {"status": "Message sent to Kafka"}
