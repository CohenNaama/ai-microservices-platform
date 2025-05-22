"""
Pydantic model for text submission.

Used for request validation in the text receiver endpoint.
"""

from pydantic import BaseModel, Field


class TextRequest(BaseModel):
    """
    Schema for incoming text payloads from client.

    Attributes:
        text (str): The message text to be sent to Kafka.
        user_id (str): Optional identifier for the user submitting the message.
    """
    text: str = Field(..., description="Text in any language, including UTF-8")
    user_id: str = Field(default="unknown", description="User ID or sender identity")
