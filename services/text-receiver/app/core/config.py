"""
Configuration loader for environment variables.

Provides access to Kafka broker URL and topic name via dotenv, with default fallbacks.
"""

import os
from dotenv import load_dotenv
from core.logging_config import logger

# Load environment variables from .env file
load_dotenv()


def get_env_variable(key: str, default: str = "") -> str:
    """
    Safely retrieve environment variable with a default fallback.

    Args:
        key (str): The name of the environment variable.
        default (str): Default value if not found.

    Returns:
        str: Value of the environment variable or default.
    """
    value = os.getenv(key, default)
    if not value:
        logger.warning(f"⚠️ Missing environment variable: {key}, using default: '{default}'")
    return value


# Kafka configuration
KAFKA_BROKER_URL: str = get_env_variable("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC: str = get_env_variable("KAFKA_TOPIC", "text-topic")
