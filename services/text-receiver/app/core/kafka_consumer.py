"""
Kafka consumer service.

Listens to Kafka topic and processes incoming messages.
Handles connection stability and message validation.
"""

import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.core.config import KAFKA_BROKER_URL, KAFKA_TOPIC
from app.core.logging_config import logger
from app.core.redis_client import set_cache
from datetime import datetime
from app.core.deduplication import is_already_processed


def process_message(message: dict) -> None:
    """
    Validates and processes a message consumed from Kafka.
    Logs, caches, and prepares the text for downstream processing.

    Args:
        message (dict): The deserialized JSON message from Kafka.

    Returns:
        None
    """

    if not isinstance(message, dict):
        logger.error("❌ Received non-dict Kafka message: %s", message)
        return

    text = message.get("text")

    if not text or not isinstance(text, str):
        logger.warning("⚠️ Invalid or missing 'text' field: %s", message)
        return

    if is_already_processed(text):
        logger.info("⚠️ Skipping duplicate text.")
        return

    logger.info("✅ Received text message: %s", text)

    # Optionally extract user_id or metadata (if exists)
    user_id = message.get("user_id", "unknown")

    # Construct cache key (e.g. for deduplication or future use)
    timestamp = datetime.utcnow().isoformat()
    cache_key = f"text:{user_id}:{timestamp}"

    # Store in Redis with TTL (10 minutes)
    cached = set_cache(cache_key, text, ttl_seconds=600)
    if not cached:
        logger.warning("⚠️ Failed to cache text message for key: %s", cache_key)
    else:
        logger.info("🧠 Message cached under key: %s", cache_key)


def get_kafka_consumer() -> KafkaConsumer:
    """
    Creates and returns a configured KafkaConsumer instance.

    Returns:
        KafkaConsumer: The consumer object.
    """
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="text-receiver-group"
    )


def start_consumer() -> None:
    """
    Initializes and runs the Kafka consumer loop.

    Listens for messages and routes them for processing.
    """
    try:
        consumer = get_kafka_consumer()
        logger.info("📡 Listening to Kafka topic '%s' on %s", KAFKA_TOPIC, KAFKA_BROKER_URL)

        for msg in consumer:
            try:
                process_message(msg.value)
            except Exception as e:
                logger.exception("❌ Failed to process message: %s", e)

    except KafkaError as e:
        logger.critical("❌ Kafka connection failed: %s", e)
    except KeyboardInterrupt:
        logger.info("🛑 Consumer stopped by user.")


if __name__ == "__main__":
    start_consumer()
