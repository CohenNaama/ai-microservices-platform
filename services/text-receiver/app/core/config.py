"""
Configuration loader for environment variables.

Provides access to Kafka broker URL and topic name via dotenv, with default fallbacks.
"""

import os
from dotenv import load_dotenv
from app.core.logging_config import logger


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
        logger.warning(f"Missing environment variable: {key}, using default: '{default}'")
    return value


def is_running_in_docker() -> bool:
    """
    Detects whether the code is running inside a Docker container.

    Returns:
        bool: True if running in Docker, False otherwise.
    """
    return os.path.exists("/.dockerenv")


# Kafka configuration
KAFKA_BROKER_URL = (
    "kafka:29092" if is_running_in_docker() else "localhost:9092"
)

KAFKA_TOPIC: str = get_env_variable("TEXT_RECEIVER_TOPIC", "text-topic")
