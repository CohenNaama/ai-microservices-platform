# app/api/routes.py
from fastapi import APIRouter
from app.models.input import TextRequest

router = APIRouter()


@router.post("/text")
def receive_text(payload: TextRequest):
    return {"received_text": payload.text}
