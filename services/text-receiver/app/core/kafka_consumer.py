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


def process_message(message: dict) -> None:
    """
    Validates and processes a message consumed from Kafka.

    Args:
        message (dict): The deserialized JSON message from Kafka.
    """
    if "text" not in message:
        logger.warning("⚠️ Message missing 'text' field: %s", message)
        return

    logger.info("✅ Received text message: %s", message["text"])
    # Add future logic here (e.g. DB store, NLP pipeline)


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
