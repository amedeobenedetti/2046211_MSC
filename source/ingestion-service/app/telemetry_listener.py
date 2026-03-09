# import asyncio
# import json
# import logging

# from app.simulator_client import SimulatorClient
# from app.common.rabbitmq_config import (
#     RABBITMQ_EXCHANGE,
#     SIMULATOR_BASE_URL
# )
# from app.common.rabbitmq_config import RabbitMQPublisher
# from app.normalizer import normalize_topic_event

# logger = logging.getLogger(__name__)


# async def telemetry_listener():

#     simulator = SimulatorClient(SIMULATOR_BASE_URL)

#     publisher = RabbitMQPublisher(exchange=RABBITMQ_EXCHANGE)
#     publisher.connect()

#     topics = await simulator.get_telemetry_topics()

#     logger.info("Discovered telemetry topics: %s", topics)

#     tasks = []

#     for topic in topics:
#         tasks.append(_listen_topic(simulator, publisher, topic))

#     await asyncio.gather(*tasks)


# async def _listen_topic(simulator, publisher, topic):

#     print(f"Listening to topic: {topic}", flush=True)

#     async for raw_event in simulator.stream_telemetry(topic):

#         payload = json.loads(raw_event)

#         logger.debug(
#             "Received telemetry event topic=%s payload=%s",
#             topic,
#             payload,
#         )

#         # event = normalize_topic_event(topic, payload)

#         # publisher.publish(
#         #     f"{RABBITMQ_TOPIC_ROUTING_KEY}.{topic}",
#         #     event.model_dump(mode="json"),
#         # )

#         # logger.info(
#         #     "Published telemetry event topic=%s event_id=%s",
#         #     topic,
#         #     event.event_id,
#         # 

import asyncio
import json
import logging

from app.simulator_client import SimulatorClient
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    SIMULATOR_BASE_URL,
    RABBITMQ_TELEMETRY_SENSORS_ROUTING_KEY
)
from app.common.rabbitmq_config import RabbitMQPublisher
from app.normalizer import normalize_topic_event

logger = logging.getLogger(__name__)

# Mappa topic -> schema_family (come da SCHEMA_CONTRACT)
TOPIC_SCHEMA_MAP = {
    "mars/telemetry/solar_array":       "topic.power.v1",
    "mars/telemetry/radiation":         "topic.environment.v1",
    "mars/telemetry/life_support":      "topic.environment.v1",
    "mars/telemetry/thermal_loop":      "topic.thermal_loop.v1",
    "mars/telemetry/power_bus":         "topic.power.v1",
    "mars/telemetry/power_consumption": "topic.power.v1",
    "mars/telemetry/airlock":           "topic.airlock.v1",
}


async def telemetry_listener():
    simulator = SimulatorClient(SIMULATOR_BASE_URL)

    publisher = RabbitMQPublisher(exchange=RABBITMQ_EXCHANGE)
    publisher.connect()

    topics = await simulator.get_telemetry_topics()
    logger.info("Discovered telemetry topics: %s", topics)

    tasks = [_listen_topic(simulator, publisher, topic) for topic in topics]
    await asyncio.gather(*tasks)


async def _listen_topic(simulator: SimulatorClient, publisher: RabbitMQPublisher, topic: str):
    logger.info("Listening to topic: %s", topic)

    schema_family = TOPIC_SCHEMA_MAP.get(topic)
    if not schema_family:
        logger.warning("No schema_family mapped for topic=%s, skipping", topic)
        return

    async for raw_event in simulator.stream_telemetry(topic):
        try:
            payload = json.loads(raw_event)

            logger.info("Received telemetry event topic=%s payload=%s", topic, payload)

            event = normalize_topic_event(topic, schema_family, payload)

            routing_key = f"{RABBITMQ_TELEMETRY_SENSORS_ROUTING_KEY}.{topic}"
            publisher.publish(routing_key, event.model_dump(mode="json"))

            logger.info(
                "Published telemetry event topic=%s event_id=%s",
                topic,
                event.event_id,
            )

        except json.JSONDecodeError as e:
            logger.error("Failed to decode JSON for topic=%s: %s", topic, e)
        except ValueError as e:
            logger.error("Normalization error for topic=%s: %s", topic, e)
        except Exception as e:
            logger.exception("Unexpected error for topic=%s: %s", topic, e)