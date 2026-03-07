import asyncio
import logging
import pika

from app.common.rabbitmq_config import (
    POLL_INTERVAL_SECONDS,
    SIMULATOR_BASE_URL,
    RABBITMQ_EXCHANGE,
    RABBITMQ_HOST,
    RABBITMQ_PASS,
    RABBITMQ_PORT,
    RABBITMQ_REST_SENSORS_ROUTING_KEY,
    RABBITMQ_USER,
)

from app.normalizer import normalize_rest_sensor
from app.common.rabbitmq_config import RabbitMQPublisher
from app.simulator_client import SimulatorClient

logger = logging.getLogger(__name__)


async def _connect_rabbitmq():

    while True:
        try:
            publisher = RabbitMQPublisher(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                username=RABBITMQ_USER,
                password=RABBITMQ_PASS,
                exchange=RABBITMQ_EXCHANGE,
            )

            publisher.connect()

            logger.info("Connected to RabbitMQ")

            return publisher

        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ not ready yet, retrying in 5 seconds...")
            await asyncio.sleep(5)


async def polling_loop():

    simulator = SimulatorClient(SIMULATOR_BASE_URL)
    publisher = await _connect_rabbitmq()
    discovery = await simulator.get_discovery()
    rest_sensors = discovery["rest_sensors"]

    logger.info(
        "Discovered REST sensors: %s",
        [s["sensor_id"] for s in rest_sensors],
    )

    while True:
        try:
            for sensor in rest_sensors:
                sensor_id = sensor["sensor_id"]
                path = sensor["path"]
                schema_family = sensor["schema_id"]

                payload = await simulator.get_sensor_by_path(path)

                event = normalize_rest_sensor(
                    sensor_id,
                    schema_family,
                    payload,
                )

                publisher.publish(f"{RABBITMQ_REST_SENSORS_ROUTING_KEY}.{sensor_id}", event.model_dump(mode="json"))

                logger.info(
                    "Published event_id=%s source=%s schema=%s",
                    event.event_id,
                    event.source_name,
                    event.schema_family,
                )

        except Exception as exc:
            logger.exception("Polling iteration failed: %s", exc)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)