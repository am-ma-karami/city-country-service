from kafka import KafkaProducer
import json
import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "city-logs")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_log(message: dict):
    producer.send(TOPIC_NAME, message)
    producer.flush()