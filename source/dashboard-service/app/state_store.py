from threading import Lock
from typing import Any

from app.common.models import MeasurementEvent, UnifiedEvent, ActuatorEvent


class StateStore:
    """In-memory store for the latest event from each source"""
    def __init__(self) -> None:
        self._lock = Lock() # Avoid reading/writing concurrently
        self._state: dict[str, dict[str, Any]] = {}

    def update_event(self, event: MeasurementEvent) -> None:
        event.source_name = event.source_name[event.source_name.rfind("/") + 1 :] if event.source_name.startswith("mars") else event.source_name

        with self._lock:
            self._state[event.source_name] = {
                "event_id": event.event_id,
                "source_kind": event.source_kind,
                "source_name": event.source_name,
                "schema_family": event.schema_family,
                "timestamp": event.timestamp.isoformat(),
                "status": event.status,
                "measurements": [
                    {
                        "metric": m.metric,
                        "value": m.value,
                        "unit": m.unit,
                    }
                    for m in event.measurements
                ],
            }
    
    def add_event(self, event: UnifiedEvent):
        with self._lock:
            if event.event_type == "actuator":
                
                ac_event = ActuatorEvent.model_validate(event.event_payload)
                if ac_event.rule_id == -1:
                    return
                
                if self._state.get("ac_notifications", None) is None:
                    self._state["ac_notifications"] = {}
                
                self._state["ac_notifications"]["source_kind"] = "ac_notification"
                self._state["ac_notifications"]["notif"] = {}
                self._state["ac_notifications"]["notif"][ac_event.rule_id] = {
                    "event_id": ac_event.event_id,
                    "actuator_name": ac_event.actuator_name,
                    "target_state": ac_event.target_state,
                    "rule_id": ac_event.rule_id,
                    "rule_name": ac_event.rule_name,
                    "sensor_name": ac_event.sensor_name
                }


    def get_all(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            ris = dict(self._state)
            if self._state.get("ac_notifications", None) is not None:
                self._state["ac_notifications"] = {}
            return ris 

    def get_one(self, source_name: str) -> dict[str, Any] | None:
        with self._lock:
            return self._state.get(source_name)