from datetime import datetime, timezone
from uuid import uuid4

from app.models import Measurement, UnifiedEvent


def _parse_timestamp(raw_timestamp: str | None) -> datetime:
    if not raw_timestamp:
        return datetime.now(timezone.utc)

    try:
        return datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def normalize_scalar_sensor(source_name: str, payload: dict) -> UnifiedEvent:
    return UnifiedEvent(
        event_id=str(uuid4()),
        source_kind="rest_sensor",
        source_name=source_name,
        schema_family="rest.scalar.v1",
        timestamp=_parse_timestamp(payload.get("timestamp")),
        status=payload.get("status", "ok"),
        measurements=[
            Measurement(
                metric=payload.get("metric", source_name),
                value=float(payload["value"]),
                unit=payload.get("unit", ""),
            )
        ],
    )