"""
Redis client integration.

Provides a reusable and validated interface for caching and key-value operations,
with full error handling and logging.
"""

import redis
from redis.exceptions import RedisError, ConnectionError
from app.core.config import get_env_variable
from app.core.logging_config import logger

# Load Redis URL from environment
REDIS_URL: str = get_env_variable("REDIS_URL", "redis://redis:6379")

try:
    # Initialize Redis client
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
    logger.info(f"Connected to Redis at {REDIS_URL}")
except (ConnectionError, RedisError) as e:
    logger.critical(f"Failed to connect to Redis: {e}")


def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """
    Stores a value in Redis with an optional TTL.

    Args:
        key (str): Redis key (non-empty).
        value (str): Value to store.
        ttl_seconds (int): Time to live in seconds (default: 1 hour).

    Returns:
        bool: True if the value was set successfully, False otherwise.
    """
    if not key or not isinstance(key, str):
        logger.warning("Invalid Redis key: %s", key)
        return False

    if not isinstance(value, str):
        logger.warning("Redis value must be a string. Got: %s", type(value))
        return False

    try:
        redis_client.set(name=key, value=value, ex=ttl_seconds)
        logger.info("Cached key '%s' (TTL: %ds)", key, ttl_seconds)
        return True
    except RedisError as e:
        logger.exception("Failed to set Redis key '%s': %s", key, e)
        return False


def get_cache(key: str) -> str | None:
    """
    Retrieves a value from Redis by key.

    Args:
        key (str): The key to look up.

    Returns:
        str | None: The stored value, or None if not found or on error.
    """
    if not key:
        logger.warning("Redis get: empty key provided.")
        return None

    try:
        value = redis_client.get(name=key)
        if value is None:
            logger.info("Redis key '%s' not found.", key)
        else:
            logger.info("Redis hit for key '%s'", key)
        return value
    except RedisError as e:
        logger.exception("Failed to get Redis key '%s': %s", key, e)
        return None


def delete_cache(key: str) -> bool:
    """
    Deletes a key from Redis.

    Args:
        key (str): The key to delete.

    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    try:
        result = redis_client.delete(key)
        if result:
            logger.info("Redis key '%s' deleted.", key)
            return True
        else:
            logger.info("Redis key '%s' not found to delete.", key)
            return False
    except RedisError as e:
        logger.exception("Failed to delete Redis key '%s': %s", key, e)
        return False
