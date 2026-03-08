import logging
from contextlib import asynccontextmanager
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    RABBITMQ_REST_SENSORS_ROUTING_KEY
)
from app.handlers import handle_measurement_event
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.rules_repository import RulesRepository
from app.common.rabbitmq_config import RabbitMQConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


consumer = None

def run_consumer() -> None:
    global consumer
    consumer = RabbitMQConsumer(RABBITMQ_EXCHANGE, [f"{RABBITMQ_REST_SENSORS_ROUTING_KEY}.greenhouse_temperature"], handle_measurement_event)
    consumer.connect()
    run_in_threadpool(consumer.start_consuming())
    print("Consumer started")


import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
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
    rules = repo.get_enabled_rules()

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



from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:8002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
