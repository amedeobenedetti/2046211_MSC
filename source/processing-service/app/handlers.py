import logging

from typing import Any
from app.common.models import UnifiedEvent
from app.state_store import StateStore

logger = logging.getLogger(__name__)

state_store = StateStore()

def store_unified_event(event: UnifiedEvent) -> None:
    state_store.update_event(event)

    logger.info(
        "Updated latest state event_id=%s source_name=%s schema_family=%s status=%s",
        event.event_id,
        event.source_name,
        event.schema_family,
        event.status,
    )

def get_state() -> dict[str, dict[str, Any]]:
    return state_store.get_all()

def get_state_by_source(source_name: str) -> dict[str, Any] | None:
    return state_store.get_one(source_name)