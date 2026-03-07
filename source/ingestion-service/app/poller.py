import asyncio
import logging
import pika

from app.config import (
    POLL_INTERVAL_SECONDS,
    SENSOR_NAME,
    SIMULATOR_BASE_URL,
    RABBITMQ_EXCHANGE,
    RABBITMQ_HOST,
    RABBITMQ_PASS,
    RABBITMQ_PORT,
    RABBITMQ_QUEUE,
    RABBITMQ_ROUTING_KEY,
    RABBITMQ_USER,
)
from app.normalizer import normalize_scalar_sensor
from app.rabbitmq import RabbitMQPublisher
from app.simulator_client import SimulatorClient

logger = logging.getLogger(__name__)


async def _connect_rabbitmq_with_retry() -> RabbitMQPublisher:
    while True:
        try:
            publisher = RabbitMQPublisher(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                username=RABBITMQ_USER,
                password=RABBITMQ_PASS,
                exchange=RABBITMQ_EXCHANGE,
                queue=RABBITMQ_QUEUE,
                routing_key=RABBITMQ_ROUTING_KEY,
            )
            publisher.connect()
            logger.info("Connected to RabbitMQ")
            return publisher
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ not ready yet, retrying in 3 seconds...")
            await asyncio.sleep(3)
        except Exception as exc:
            logger.exception("Unexpected RabbitMQ connection error: %s", exc)
            await asyncio.sleep(3)


async def polling_loop() -> None:
    simulator = SimulatorClient(SIMULATOR_BASE_URL)
    publisher = await _connect_rabbitmq_with_retry()

    while True:
        try:
            raw_payload = await simulator.get_sensor(SENSOR_NAME)
            event = normalize_scalar_sensor(SENSOR_NAME, raw_payload)

            publisher.publish(event.model_dump(mode="json"))
            logger.info(
                "Published event_id=%s source_name=%s schema_family=%s",
                event.event_id,
                event.source_name,
                event.schema_family,
            )
        except Exception as exc:
            logger.exception("Polling iteration failed: %s", exc)

            # se RabbitMQ cade dopo essere stato connesso, prova a riconnettere
            try:
                publisher.close()
            except Exception:
                pass

            publisher = await _connect_rabbitmq_with_retry()

        await asyncio.sleep(POLL_INTERVAL_SECONDS)