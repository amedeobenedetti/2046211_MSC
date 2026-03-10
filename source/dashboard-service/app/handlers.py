import logging
from uuid import uuid4
from typing import Any
from app.common.models import UnifiedEvent, MeasurementEvent, ActuatorEvent, RuleEvent
from app.state_store import StateStore
from app.common.rabbitmq_config import RabbitMQPublisher, RABBITMQ_ACTUATOR_ROUTING_KEY, RABBITMQ_RULES_ROUTING_KEY

publisher = RabbitMQPublisher()
publisher.connect()


logger = logging.getLogger(__name__)

state_store = StateStore()

def handle_measurement_event(event: UnifiedEvent) -> None:
    if event.event_type != "measurement":
        logger.warning("Received non-measurement event: event_id=%s", event.event_id)
        return 

    m_event = MeasurementEvent.model_validate(event.event_payload)

    state_store.update_event(m_event) # Update the state store with the latest event data

    logger.info(
        "Updated latest state event_id=%s source_name=%s schema_family=%s status=%s",
        m_event.event_id,
        m_event.source_name,
        m_event.schema_family,
        m_event.status,
    )

def handle_actuator_event(event: UnifiedEvent) -> None:
    logger.info("Received actuator event: event_id=%s", event.event_id)
    if event.event_type != "actuator":
        logger.warning("Received non-actuator event: event_id=%s", event.event_id)
        return 
    state_store.add_event(event)



def get_state() -> dict[str, dict[str, Any]]:
    return state_store.get_all()

def get_state_by_source(source_name: str) -> dict[str, Any] | None:
    return state_store.get_one(source_name)

def send_actuator_command(actuator_name: str, command: str) -> None:
    a_event = ActuatorEvent(
        event_id=str(uuid4()),
        rule_id=-1,
        rule_name="manual",
        sensor_name="manual",
        metric_name="manual",
        actuator_name=actuator_name,
        target_state=command,
        measured_value=0.0,
        threshold_value=0.0,
        operator="manual",
        unit="manual",
    )

    new_event = UnifiedEvent(
            event_id=a_event.event_id,
            event_type="actuator",
            event_payload=a_event)

    publisher.publish(
            RABBITMQ_ACTUATOR_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
        
    logger.info("Published actuator event: event_id=%s", new_event.event_id)

def set_rule_state(rule_id: int, new_state: bool) -> None:
    r_event = RuleEvent(
        event_id=str(uuid4()),
        operation="toggle",
        rule_id=rule_id,
        rule_enabled=new_state,
    )

    new_event = UnifiedEvent(
            event_id=r_event.event_id,
            event_type="rules",
            event_payload=r_event)

    publisher.publish(
            RABBITMQ_RULES_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
    logger.info("Setting rule state: rule_id=%d new_state=%s", rule_id, new_state)

def add_rule(rule: dict) -> None:
    rule = rule.get("rule", None) if rule.get("rule", None) is not None else rule
    rule["rule_name"] = rule.get("name", "new_rule")
    rule["rule_enabled"] = rule.get("enabled", True)

    r_event = RuleEvent(
        event_id=str(uuid4()),
        operation="add",
        **rule
    )

    new_event = UnifiedEvent(
            event_id=r_event.event_id,
            event_type="rules",
            event_payload=r_event)

    publisher.publish(
            RABBITMQ_RULES_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
    return {"status": "ok", "rule": rule, "event_rule": r_event.model_dump_json()}


def update_rule(rule: dict) -> dict:

    rule["rule_id"] = rule["id"]
    rule["rule_name"] = rule["name"]
    
    r_event = RuleEvent(
        event_id=str(uuid4()),
        operation="update",
        **rule
    )

    new_event = UnifiedEvent(
            event_id=r_event.event_id,
            event_type="rules",
            event_payload=r_event)

    publisher.publish(
            RABBITMQ_RULES_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
    return {"status": "ok", "rule": rule}

def delete_rule(rule_id: int) -> None:
    r_event = RuleEvent(
        event_id=str(uuid4()),
        operation="delete",
        rule_id=rule_id
    )

    new_event = UnifiedEvent(
            event_id=r_event.event_id,
            event_type="rules",
            event_payload=r_event)

    publisher.publish(
            RABBITMQ_RULES_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
    return {"status": "ok", 'rule_id': rule_id}

    