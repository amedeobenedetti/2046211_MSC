from datetime import datetime, timezone
from uuid import uuid4

from app.common.models import Measurement, MeasurementEvent, UnifiedEvent


def _parse_timestamp(ts: str | None) -> datetime:

    if not ts:
        return datetime.now(timezone.utc)

    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _build_event(source_name, schema_family, payload, measurements):
    event = MeasurementEvent(
        event_id=str(uuid4()),
        source_kind="rest_sensor",
        source_name=source_name,
        schema_family=schema_family,
        timestamp=_parse_timestamp(payload.get("timestamp")),
        status=payload.get("status", "ok"),
        measurements=measurements,
    )
    return UnifiedEvent(
        event_id=event.event_id,
        event_type="measurement",
        event_payload=event)


def normalize_scalar_sensor(source_name, schema_family, payload):

    return _build_event(
        source_name,
        schema_family,
        payload,
        [
            Measurement(
                metric=payload.get("metric", source_name),
                value=float(payload["value"]),
                unit=payload.get("unit", ""),
            )
        ],
    )


def normalize_chemistry_sensor(source_name, schema_family, payload):

    measurements = []

    for m in payload.get("measurements", []):
        measurements.append(
            Measurement(
                metric=m["metric"],
                value=float(m["value"]),
                unit=m.get("unit", ""),
            )
        )

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_level_sensor(source_name, schema_family, payload):

    measurements = []

    if "level_pct" in payload:
        measurements.append(
            Measurement(metric="level_pct", value=float(payload["level_pct"]), unit="%")
        )

    if "level_liters" in payload:
        measurements.append(
            Measurement(metric="level_liters", value=float(payload["level_liters"]), unit="L")
        )

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_particulate_sensor(source_name, schema_family, payload):

    measurements = []

    if "pm1_ug_m3" in payload:
        measurements.append(
            Measurement(metric="pm1", value=float(payload["pm1_ug_m3"]), unit="ug/m3")
        )

    if "pm25_ug_m3" in payload:
        measurements.append(
            Measurement(metric="pm25", value=float(payload["pm25_ug_m3"]), unit="ug/m3")
        )

    if "pm10_ug_m3" in payload:
        measurements.append(
            Measurement(metric="pm10", value=float(payload["pm10_ug_m3"]), unit="ug/m3")
        )

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_rest_sensor(source_name, schema_family, payload):

    if schema_family == "rest.scalar.v1":
        return normalize_scalar_sensor(source_name, schema_family, payload)

    if schema_family == "rest.chemistry.v1":
        return normalize_chemistry_sensor(source_name, schema_family, payload)

    if schema_family == "rest.level.v1":
        return normalize_level_sensor(source_name, schema_family, payload)

    if schema_family == "rest.particulate.v1":
        return normalize_particulate_sensor(source_name, schema_family, payload)

    raise ValueError(f"Unsupported schema {schema_family}")