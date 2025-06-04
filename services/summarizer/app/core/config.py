"""
Configuration loader for environment variables.

Provides access to Kafka broker URL and topic names via dotenv,
with default fallbacks and Docker auto-detection.
"""

import os
from dotenv import load_dotenv
from app.core.logging_config import logger

# Load .env file variables
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


# Kafka broker: docker uses 'kafka:29092', local uses 'localhost:9092'
KAFKA_BROKER_URL = "kafka:29092" if is_running_in_docker() else "localhost:9092"

# Kafka topics
SUMMARIZER_INPUT_TOPIC = get_env_variable("SUMMARIZER_INPUT_TOPIC", "text-topic")
KAFKA_CONSUME_TOPIC: str = SUMMARIZER_INPUT_TOPIC


SUMMARIZER_OUTPUT_TOPIC = get_env_variable("SUMMARIZER_OUTPUT_TOPIC", "summarized-texts")
KAFKA_PRODUCE_TOPIC: str = SUMMARIZER_OUTPUT_TOPIC

# OpenAI
OPENAI_API_KEY: str = get_env_variable("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. OpenAI integration will likely fail.")
