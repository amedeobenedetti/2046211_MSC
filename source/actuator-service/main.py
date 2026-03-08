import logging
from contextlib import asynccontextmanager
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    RABBITMQ_ACTUATOR_ROUTING_KEY
)
from app.handlers import handle_actuator_event
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool

from app.common.rabbitmq_config import RabbitMQConsumer

from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


consumer = None

def run_consumer() -> None:
    global consumer
    consumer = RabbitMQConsumer("actuator",RABBITMQ_EXCHANGE, [f"{RABBITMQ_ACTUATOR_ROUTING_KEY}"], handle_actuator_event)
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


app = FastAPI(title="Actuator Service", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}