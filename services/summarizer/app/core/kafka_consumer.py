"""
Kafka consumer for the Summarizer microservice.

Consumes raw text messages from Kafka, summarizes them using OpenAI,
and publishes the summarized result to a Kafka topic.
"""

import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from core.config import KAFKA_BROKER_URL, KAFKA_CONSUME_TOPIC, KAFKA_PRODUCE_TOPIC
from core.summarizer_service import summarize_text
from core.logging_config import logger


def _consume_loop() -> None:
    """
    Starts the Kafka consumer loop.

    Listens to the configured topic for new text messages, processes them by summarizing,
    and publishes the result to a separate Kafka topic.

    This loop runs in a dedicated background thread.
    """
    logger.info("🔁 Initializing Kafka consumer...")

    try:
        consumer = KafkaConsumer(
            KAFKA_CONSUME_TOPIC,
            bootstrap_servers=KAFKA_BROKER_URL,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="summarizer-group"
        )

        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
        )

        logger.info(f"🎧 Listening to Kafka topic: '{KAFKA_CONSUME_TOPIC}'")

        for msg in consumer:
            try:
                _process_message(msg.value, producer)
            except Exception as e:
                logger.exception("❌ Error while processing Kafka message: %s", e)

    except KafkaError as e:
        logger.critical("❌ Kafka connection failed: %s", e)
    except Exception as e:
        logger.exception("❌ Unexpected error in Kafka consumer loop: %s", e)


def _process_message(message: dict, producer: KafkaProducer) -> None:
    """
    Processes a single Kafka message.

    Args:
        message (dict): The message received from Kafka.
        producer (KafkaProducer): Kafka producer used to send summarized output.

    Returns:
        None
    """
    logger.debug("📥 Received message from Kafka: %s", message)

    if not isinstance(message, dict):
        logger.error("❌ Invalid message format: expected JSON object.")
        return

    text = message.get("text")
    user_id = message.get("user_id", "unknown")
    text_id = message.get("text_id")  # Optional, may be None

    if not text or not isinstance(text, str) or not text.strip():
        logger.warning("⚠️ Message missing valid 'text' field: %s", message)
        return

    logger.info("🧠 Summarizing text for user '%s', text_id='%s'", user_id, text_id)

    summary = summarize_text(text)

    result = {
        "user_id": user_id,
        "text_id": text_id,
        "summary": summary
    }

    try:
        producer.send(KAFKA_PRODUCE_TOPIC, value=result)
        producer.flush()
        logger.info("✅ Published summary to topic '%s' for user '%s'", KAFKA_PRODUCE_TOPIC, user_id)
    except KafkaError as e:
        logger.exception("❌ Failed to publish summary to Kafka: %s", e)
