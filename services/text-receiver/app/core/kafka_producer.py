from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "text-topic")

# Initialize a global KafkaProducer instance
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def send_text_to_kafka(data: dict) -> bool:
    """
    Sends a dictionary as JSON to the Kafka topic.
    """
    try:
        producer.send(KAFKA_TOPIC, value=data)
        producer.flush()  # Optional for guaranteed delivery
        return True
    except KafkaError as e:
        # Optional: add logging here
        print(f"❌ Kafka send error: {e}")
        return False
