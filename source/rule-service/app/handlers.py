import logging
from typing import Any
from app.common.models import UnifiedEvent, MeasurementEvent
from app.common.rabbitmq_config import RabbitMQPublisher, RABBITMQ_ACTUATOR_ROUTING_KEY
from app.rule_engine import RuleEngine
from app.rules_repository import RulesRepository

logger = logging.getLogger(__name__)

rules_repository = RulesRepository()
rule_engine = RuleEngine()

publisher = RabbitMQPublisher()
publisher.connect()

def handle_measurement_event(event: UnifiedEvent) -> None:
    logger.info("Received event: event_id=%s", event.event_id)
    if event.event_type != "measurement":
        logger.warning("Received non-measurement event: event_id=%s", event.event_id)
        return
    
    m_event = MeasurementEvent.model_validate(event.event_payload)
    
    # Evaluate rules for the event's source and trigger any that are satisfied
    rules = rules_repository.get_enabled_rules_for_sensor(m_event.source_name)
  
    triggered_rules = rule_engine.evaluate_event(m_event, rules)

    print(f'Event {m_event.event_id} triggered {len(triggered_rules)} rules for {m_event.source_name}', flush=True)
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

        # rabbita verso dashboard