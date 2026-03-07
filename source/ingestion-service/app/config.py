import os

SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://mars-simulator:8080")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "mars")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "mars")

RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "mars.events")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "sensor.rest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "sensor.events")

POLL_INTERVAL_SECONDS = float(os.getenv("POLL_INTERVAL_SECONDS", "5"))
SENSOR_NAME = os.getenv("SENSOR_NAME", "greenhouse_temperature")