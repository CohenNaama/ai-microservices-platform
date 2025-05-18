# app/models/input.py
from pydantic import BaseModel


class TextRequest(BaseModel):
    text: str
