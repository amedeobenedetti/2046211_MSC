import os
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://mars-simulator:8080")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "mars")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "mars")

RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "mars.events") 
RABBITMQ_REST_SENSORS_ROUTING_KEY = os.getenv("RABBITMQ_REST_SENSORS_ROUTING_KEY", "sensor.rest")
RABBITMQ_ACTUATOR_ROUTING_KEY = os.getenv("RABBITMQ_ACTUATOR_ROUTING_KEY", "actuator.trigger")

POLL_INTERVAL_SECONDS = float(os.getenv("POLL_INTERVAL_SECONDS", "5"))

import json
import pika
from app.common.models import UnifiedEvent
from pydantic import ValidationError




class RabbitMQPublisher:
    def __init__(
        self,
        exchange: str = RABBITMQ_EXCHANGE,
    ):
        
        self.exchange = exchange
        self.connection = None
        self.channel = None



    def connect(self) -> None:

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )

        while True:
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type="topic",
                    durable=True,
                )

                logger.info("Connected to RabbitMQ")

                return

            except pika.exceptions.AMQPConnectionError:
                logger.warning("RabbitMQ not ready yet, retrying in 3 seconds...")
                time.sleep(3)
    

    def publish(self, routing_key: str, payload: dict) -> None:
        if self.channel is None:
            raise RuntimeError("RabbitMQ channel is not connected")

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=json.dumps(payload, default=str).encode("utf-8"),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )

    def close(self) -> None:
        if self.connection and self.connection.is_open:
            self.connection.close()


class RabbitMQConsumer:

    def __init__(self, exchange: str, routing_keys: list[str], callback_func: Callable) -> None:
        self.routing_keys = routing_keys
        self.connection = None
        self.channel = None
        self.exchange = exchange
        self.callback_func = callback_func




    def connect(self) -> None:

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
        )

        while True:
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                self.channel.exchange_declare(
                    exchange=self.exchange,
                    exchange_type="topic",
                    durable=True,
                )

                logger.info("Connected to RabbitMQ")

                self._declare_queues()

                return

            except pika.exceptions.AMQPConnectionError:
                logger.warning("RabbitMQ not ready yet, retrying in 3 seconds...")
                time.sleep(3)

    def _declare_queues(self) -> None:

        for routing_key in self.routing_keys:

            queue_name = f"routings.{routing_key}.events"

            self.channel.queue_declare(
                queue=queue_name,
                durable=False,
            )

            self.channel.queue_bind(
                exchange=RABBITMQ_EXCHANGE,
                queue=queue_name,
                routing_key=routing_key,
            )

            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_message,
            )

            logger.info(
                "Queue created queue=%s bound_to=%s",
                queue_name,
                routing_key,
            )

    def _on_message(self, ch, method, properties, body: bytes) -> None:

        try:

            payload = json.loads(body.decode("utf-8"))

            event = UnifiedEvent.model_validate(payload)

            self.callback_func(event)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except ValidationError as exc:

            logger.exception("Invalid UnifiedEvent payload: %s", exc)

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

        except Exception as exc:

            logger.exception("Unexpected consumer error: %s", exc)

            ch.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=True,
            )

    def start_consuming(self) -> None:

        if self.channel is None:
            raise RuntimeError("Consumer channel not connected")

        logger.info("Consumer started")

        self.channel.start_consuming()

    def close(self) -> None:

        if self.connection and self.connection.is_open:
            self.connection.close()