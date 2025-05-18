"""
Pydantic model for text submission.

Used for request validation in the text receiver endpoint.
"""

from pydantic import BaseModel


class TextRequest(BaseModel):
    """
    Schema for incoming text payloads from client.

    Attributes:
        text (str): The message text to be sent to Kafka.
    """
    text: str

