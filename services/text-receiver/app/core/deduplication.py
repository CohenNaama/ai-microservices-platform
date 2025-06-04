"""
Deduplication logic using Redis and SHA256 hashing.

Prevents re-processing of identical messages across the system.
"""

import hashlib
from app.core.redis_client import get_cache, set_cache
from app.core.logging_config import logger


def is_already_processed(text: str) -> bool:
    """
    Checks if the given text was already processed using a Redis hash key.

    Args:
        text (str): The input text to check.

    Returns:
        bool: True if already processed, False otherwise.
    """
    if not text or not isinstance(text, str):
        logger.warning("is_already_processed received invalid text input.")
        return False

    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    cache_key = f"processed:{text_hash}"

    existing = get_cache(cache_key)
    if existing:
        logger.info("Text already processed [hash=%s]", text_hash)
        return True

    # Mark as processed
    set_cache(cache_key, "1", ttl_seconds=3600)
    logger.debug("Marked text as processed [hash=%s]", text_hash)
    return False
