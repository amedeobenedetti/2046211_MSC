import logging
from contextlib import asynccontextmanager
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    RABBITMQ_REST_SENSORS_ROUTING_KEY
)
from app.handlers import store_unified_event, get_state, get_state_by_source
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.common.rabbitmq_config import RabbitMQConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

consumer = None

def run_consumer() -> None:
    global consumer
    consumer = RabbitMQConsumer(RABBITMQ_EXCHANGE, [f"{RABBITMQ_REST_SENSORS_ROUTING_KEY}.#"], store_unified_event)
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


app = FastAPI(title="Consumer Service", version="0.1.0", lifespan=lifespan)

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/state")
async def get_state_s() -> dict:
    return await run_in_threadpool(get_state)


@app.get("/state/{source_name}")
async def get_state_from_name(source_name: str) -> dict:
    def get_source(source_name:str):
        state = get_state_by_source(source_name)

        if state is None:
            raise HTTPException(status_code=404, detail="Source not found")
        return state
    return await run_in_threadpool(get_source, source_name)