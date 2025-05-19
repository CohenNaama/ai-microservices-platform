"""
Kafka producer logic.

Initializes the producer and provides a function to send validated messages to a Kafka topic.
"""

import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
from app.core.config import KAFKA_BROKER_URL, KAFKA_TOPIC
from app.core.logging_config import logger


def get_kafka_producer() -> KafkaProducer:
    """
    Creates and returns a configured KafkaProducer instance.

    Returns:
        KafkaProducer: The producer object.
    """
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )


producer = get_kafka_producer()


def send_text_to_kafka(data: dict) -> bool:
    """
    Validates and sends a message to a Kafka topic.

    Args:
        data (dict): The dictionary payload to send. Must include a 'text' field.

    Returns:
        bool: True if the message was successfully sent, False otherwise.
    """
    if not isinstance(data, dict):
        logger.error("❌ Data to send is not a dictionary: %s", data)
        return False

    if "text" not in data:
        logger.warning("⚠️ Missing required 'text' field in payload: %s", data)
        return False

    try:
        logger.debug("📤 Sending message to Kafka: %s", data)
        producer.send(KAFKA_TOPIC, value=data)
        producer.flush()
        logger.info("✅ Message sent to Kafka topic '%s'", KAFKA_TOPIC)
        return True
    except KafkaError as e:
        logger.exception("❌ Kafka send failed: %s", e)
        return False
