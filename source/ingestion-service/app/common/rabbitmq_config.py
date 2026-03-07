import os

SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://mars-simulator:8080")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "mars")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "mars")

RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "mars.events") 
RABBITMQ_REST_SENSORS_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "sensor.rest")

POLL_INTERVAL_SECONDS = float(os.getenv("POLL_INTERVAL_SECONDS", "5"))

import json
import pika


class RabbitMQPublisher:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        exchange: str,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.exchange = exchange

        self.connection = None
        self.channel = None

    def connect(self) -> None:
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type="topic",
            durable=True,
        )
        

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