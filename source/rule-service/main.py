import logging
from contextlib import asynccontextmanager
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    RABBITMQ_REST_SENSORS_ROUTING_KEY,
    RABBITMQ_RULES_ROUTING_KEY,
    RABBITMQ_TELEMETRY_SENSORS_ROUTING_KEY
)
from app.handlers import handle_measurement_event, handle_rules_event
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.rules_repository import RulesRepository
from app.common.rabbitmq_config import RabbitMQConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


sensors_consumer = None
rules_consumer = None


def run_sensors_consumer() -> None:
    global sensors_consumer
    sensors_consumer = RabbitMQConsumer("rules",RABBITMQ_EXCHANGE, [f"{RABBITMQ_REST_SENSORS_ROUTING_KEY}.#", f"{RABBITMQ_TELEMETRY_SENSORS_ROUTING_KEY}.#"], handle_measurement_event)
    sensors_consumer.connect()
    run_in_threadpool(sensors_consumer.start_consuming())
    print("Sensors Consumer started")

def run_rules_consumer() -> None:
    global rules_consumer
    rules_consumer = RabbitMQConsumer("rules",RABBITMQ_EXCHANGE, [f"{RABBITMQ_RULES_ROUTING_KEY}.#"], handle_rules_event)
    rules_consumer.connect()
    run_in_threadpool(rules_consumer.start_consuming())
    print("Rules Consumer started")
    

import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=run_sensors_consumer, daemon=True)
    thread.start()
    thread2 = threading.Thread(target=run_rules_consumer, daemon=True)
    thread2.start()
    print("Startup Completed!")
    yield
    print("Shutdown Completed!")


app = FastAPI(title="Processing Service", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

@app.get("/rules")
async def get_rules() -> list[dict]:
    repo = RulesRepository()
    rules = repo.get_rules()

    return [
        {
            "id": rule.id,
            "name": rule.name,
            "sensor_name": rule.sensor_name,
            "metric_name": rule.metric_name,
            "operator": rule.operator,
            "threshold_value": rule.threshold_value,
            "unit": rule.unit,
            "actuator_name": rule.actuator_name,
            "target_state": rule.target_state,
            "rule_enabled": rule.rule_enabled,
        }
        for rule in rules
    ]


