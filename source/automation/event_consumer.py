import pika
import json

from common.schema import UnifiedEvent
from rule_repository import get_rules
from rule_engine import evaluate_event
from actuator_client import set_actuator


connection = pika.BlockingConnection(
    pika.ConnectionParameters("rabbitmq")
)

channel = connection.channel()
channel.queue_declare(queue="sensor_events")


def callback(ch, method, properties, body):

    data = json.loads(body)

    event = UnifiedEvent(**data)

    rules = get_rules()

    triggered = evaluate_event(event, rules)

    for rule in triggered:
        set_actuator(rule.actuator_name, rule.target_state)


channel.basic_consume(
    queue="sensor_events",
    on_message_callback=callback,
    auto_ack=True
)


def start():

    print("Automation service listening for events...")
    channel.start_consuming()