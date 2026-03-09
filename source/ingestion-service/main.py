import asyncio
import logging

from fastapi import FastAPI
from app.poller import polling_loop
from app.telemetry_listener import telemetry_listener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(title="Ingestion Service", version="0.1.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
def startup_event() -> None:
    asyncio.create_task(polling_loop())
    asyncio.create_task(telemetry_listener())