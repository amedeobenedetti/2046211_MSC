from threading import Lock
from typing import Any

from app.common.models import MeasurementEvent


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

    def get_all(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            return dict(self._state)

    def get_one(self, source_name: str) -> dict[str, Any] | None:
        with self._lock:
            return self._state.get(source_name)