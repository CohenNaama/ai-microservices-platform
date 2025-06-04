"""
Kafka consumer service.

Listens to Kafka topic and processes incoming messages.
Handles connection stability and message validation.
"""

import asyncio
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.core.config import KAFKA_BROKER_URL, KAFKA_TOPIC
from app.core.logging_config import logger
from app.core.redis_client import set_cache
from datetime import datetime
from app.core.deduplication import is_already_processed
from app.core.db import SessionLocal
from app.models.db_models import ProcessedText
import reprlib


def process_message(message: dict) -> None:
    """
    Validates and processes a message consumed from Kafka.
    Performs logging, caching, deduplication, and DB storage.

    Args:
        message (dict): The deserialized JSON message from Kafka.

    Returns:
        None
    """
    # Validate structure
    if not isinstance(message, dict):
        logger.error("Received non-dict Kafka message: %s", message)
        return

    text = message.get("text")
    if not text or not isinstance(text, str):
        logger.warning("Invalid or missing 'text' field: %s", message)
        return

    logger.info(f"Sent to Kafka: {reprlib.repr(text)}")

    # Deduplication logic
    if is_already_processed(text):
        logger.info("Skipping duplicate text.")
        return

    logger.info("Received text message: %s", text)

    # Optional metadata
    user_id = message.get("user_id", "unknown")
    text_id = message.get("text_id")
    if not text_id:
        logger.warning("Received message without 'text_id'. Skipping.")
        return
    # Redis cache
    timestamp = datetime.utcnow().isoformat()
    cache_key = f"text:{user_id}:{timestamp}"
    cached = set_cache(cache_key, text, ttl_seconds=600)

    if not cached:
        logger.warning("Failed to cache text for key: %s", cache_key)
    else:
        logger.info("Text cached under key: %s", cache_key)

    # Store in PostgreSQL
    db = SessionLocal()
    try:
        record = ProcessedText(
            text_id=text_id,
            user_id=user_id,
            original_text=text
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        logger.info(
            "Text processed and saved successfully | user_id='%s' | text_id='%s' | db_id=%s",
            user_id, text_id, record.id
        )
    except Exception as e:
        db.rollback()
        logger.exception("Failed to insert text into PostgreSQL: %s", e)
    finally:
        db.close()


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


def _consume_loop():
    """
    Starts an infinite loop to consume and process Kafka messages.
    """
    consumer = get_kafka_consumer()
    logger.info("Listening to Kafka topic '%s' on %s", KAFKA_TOPIC, KAFKA_BROKER_URL)
    try:
        for msg in consumer:
            process_message(msg.value)
    except Exception as e:
        logger.exception("Kafka consumer loop crashed: %s", e)


async def start_consumer_async() -> None:
    """
    Runs the Kafka consumer loop in a background thread using asyncio.

    Returns:
        None
    """
    try:
        consumer = get_kafka_consumer()
        logger.info("Listening to Kafka topic '%s' on %s", KAFKA_TOPIC, KAFKA_BROKER_URL)

        await asyncio.to_thread(_consume_loop, consumer)

    except KafkaError as e:
        logger.critical("Kafka connection failed: %s", e)
    except asyncio.CancelledError:
        logger.info("Consumer cancelled.")
    except Exception as e:
        logger.exception("Unexpected error in Kafka consumer: %s", e)
