"""
text_summarizer.py

Handles interaction with the OpenAI API to summarize input text.
"""
import openai
from app.core.config import OPENAI_API_KEY
from app.core.logging_config import logger


def summarize_text(text: str) -> str:
    """
    Summarizes the given text using the OpenAI ChatCompletion API.

    Args:
        text (str): The input text to be summarized.

    Returns:
        str: The generated summary. Returns fallback string on error.
    """
    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("Invalid input for summarization. Must be non-empty string.")
        return "Invalid input"

    logger.info("Sending text to OpenAI for summarization...")

    try:
        response = openai.ChatCompletion.create(
            api_key=OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=100,
            messages=[
                {"role": "system", "content": "Summarize the following text briefly:"},
                {"role": "user", "content": text}
            ]
        )

        summary = response["choices"][0]["message"]["content"].strip()
        logger.info("Summary received from OpenAI.")
        return summary

    except openai.error.OpenAIError as oe:
        logger.exception("OpenAI API error: %s", oe)
        return "OpenAI summarization failed"
    except Exception as e:
        logger.exception("Unexpected error during summarization: %s", e)
        return "Summarization failed"
