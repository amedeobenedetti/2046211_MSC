import logging

from typing import Any
from app.common.models import UnifiedEvent, MeasurementEvent
from app.state_store import StateStore

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

def get_state() -> dict[str, dict[str, Any]]:
    return state_store.get_all()

def get_state_by_source(source_name: str) -> dict[str, Any] | None:
    return state_store.get_one(source_name)