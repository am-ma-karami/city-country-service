import json
import time
from kafka import KafkaProducer
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = "city-logs"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

total_requests = 0
cache_hits = 0


def log_request(duration_ms: float, cache_hit: bool):
    global total_requests, cache_hits

    total_requests += 1
    if cache_hit:
        cache_hits += 1

    message = {
        "response_time_ms": duration_ms,
        "cache_hit": cache_hit,
        "cache_hit_ratio": round(cache_hits / total_requests, 3),
        "timestamp": time.time()
    }

    producer.send(KAFKA_TOPIC, message)