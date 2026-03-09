import logging
from typing import Any
from app.common.models import UnifiedEvent, MeasurementEvent, RuleEvent
from app.common.rabbitmq_config import RabbitMQPublisher, RABBITMQ_ACTUATOR_ROUTING_KEY
from app.rule_engine import RuleEngine
from app.rules_repository import RulesRepository

logger = logging.getLogger(__name__)

rules_repository = RulesRepository()
rule_engine = RuleEngine()

publisher = RabbitMQPublisher()
publisher.connect()

def handle_measurement_event(event: UnifiedEvent) -> None:
    # logger.info("Received measurement event: event_id=%s", event.event_id)
    if event.event_type != "measurement":
        logger.warning("Received non-measurement event: event_id=%s", event.event_id)
        return
    
    m_event = MeasurementEvent.model_validate(event.event_payload)
    
    # Evaluate rules for the event's source and trigger any that are satisfied
    rules = rules_repository.get_rules_for_sensor(m_event.source_name)
  
    triggered_rules = rule_engine.evaluate_event(m_event, rules)
    # if len(triggered_rules) > 0:
    #     print(f'Event {m_event.event_id} triggered {len(triggered_rules)} rules for {m_event.source_name}', flush=True)
    for triggered in triggered_rules:
        logger.info(
            "Rule triggered rule_id=%s rule_name=%s sensor=%s metric=%s measured=%s operator=%s threshold=%s actuator=%s target_state=%s",
            triggered.rule_id,
            triggered.rule_name,
            triggered.sensor_name,
            triggered.metric_name,
            triggered.measured_value,
            triggered.operator,
            triggered.threshold_value,
            triggered.actuator_name,
            triggered.target_state,
        )
        new_event = UnifiedEvent(
            event_id=triggered.event_id,
            event_type="actuator",
            event_payload=triggered)

        publisher.publish(
            RABBITMQ_ACTUATOR_ROUTING_KEY,
            new_event.model_dump(mode="json"),
        )
        
        logger.info("Published actuator event: event_id=%s", new_event.event_id)


def handle_rules_event(event: UnifiedEvent) -> None:
    logger.info("Received rules event: event_id=%s", event.event_id)
    if event.event_type != "rules":
        logger.warning("Received non-rules event: event_id=%s", event.event_id)
        return
    
    r_event = RuleEvent.model_validate(event.event_payload)
    
    if r_event.operation == "toggle":
        logger.info("Detected toggle operation: rule_id=%s, rule_enabled=%s", str(r_event.rule_id), str(r_event.rule_enabled))
        rules_repository.set_rule_state(r_event.rule_id, r_event.rule_enabled)

    if r_event.operation == "add":
        pass
    if r_event.operation == "update":
        logger.info("Detected update operation on rule_id=%s", str(r_event.rule_id))
        old_rule = rules_repository.get_rule_from_id(r_event.rule_id)
        if old_rule is None:
            logger.warning("Rule not found: rule_id=%s", str(r_event.rule_id))
            return
        
        new_rule = old_rule
        new_rule.name = r_event.rule_name if r_event.rule_name is not None else new_rule.name
        new_rule.rule_enabled = r_event.rule_enabled if r_event.rule_enabled is not None else new_rule.rule_enabled
        new_rule.sensor_name = r_event.sensor_name if r_event.sensor_name is not None else new_rule.sensor_name
        new_rule.metric_name = r_event.metric_name if r_event.metric_name is not None else new_rule.metric_name
        new_rule.actuator_name = r_event.actuator_name if r_event.actuator_name is not None else new_rule.actuator_name
        new_rule.target_state = r_event.target_state if r_event.target_state is not None else new_rule.target_state
        new_rule.operator = r_event.operator if r_event.operator is not None else new_rule.operator
        new_rule.threshold_value = r_event.threshold_value if r_event.threshold_value is not None else new_rule.threshold_value
        new_rule.unit = r_event.unit if r_event.unit is not None else new_rule.unit
        try:
            rules_repository.update_rule(new_rule)
        except:
            logger.warning("Update failed on rule_id=%s", str(r_event.rule_id))
            return
        logger.info("Update successful on rule_id=%s", str(r_event.rule_id))
        

    if r_event.operation == "delete":
        pass

    
    