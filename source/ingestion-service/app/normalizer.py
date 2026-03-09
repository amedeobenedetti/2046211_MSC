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
    # REST sensors use "captured_at", telemetry topics use "event_time"
    ts = payload.get("captured_at") or payload.get("event_time") or payload.get("timestamp")
    event = MeasurementEvent(
        event_id=str(uuid4()),
        source_kind="rest_sensor" if schema_family.startswith("rest.") else "telemetry_topic",
        source_name=source_name,
        schema_family=schema_family,
        timestamp=_parse_timestamp(ts),
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


def normalize_topic_event(topic: str, schema_family: str, payload: dict):

    if schema_family == "topic.power.v1":
        return normalize_power_topic(topic, schema_family, payload)

    if schema_family == "topic.environment.v1":
        return normalize_environment_topic(topic, schema_family, payload)

    if schema_family == "topic.thermal_loop.v1":
        return normalize_thermal_loop_topic(topic, schema_family, payload)

    if schema_family == "topic.airlock.v1":
        return normalize_airlock_topic(topic, schema_family, payload)

    raise ValueError(f"Unsupported telemetry schema {schema_family}")


def normalize_power_topic(source_name, schema_family, payload):
    # Schema: topic.power.v1 fields: power_kw, voltage_v, current_a, cumulative_kwh
    measurements = []

    if "voltage_v" in payload:
        measurements.append(
            Measurement(metric="voltage", value=float(payload["voltage_v"]), unit="V")
        )

    if "current_a" in payload:
        measurements.append(
            Measurement(metric="current", value=float(payload["current_a"]), unit="A")
        )

    if "power_kw" in payload:
        measurements.append(
            Measurement(metric="power", value=float(payload["power_kw"]), unit="kW")
        )

    if "cumulative_kwh" in payload:
        measurements.append(
            Measurement(metric="cumulative_energy", value=float(payload["cumulative_kwh"]), unit="kWh")
        )

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_environment_topic(source_name, schema_family, payload):
    # Schema: topic.environment.v1 fields: measurements (array of {metric, value, unit})
    measurements = [
        Measurement(
            metric=m["metric"],
            value=float(m["value"]),
            unit=m.get("unit", ""),
        )
        for m in payload.get("measurements", [])
    ]

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_thermal_loop_topic(source_name, schema_family, payload):
    # Schema: topic.thermal_loop.v1 fields: temperature_c, flow_l_min
    measurements = []

    if "temperature_c" in payload:
        measurements.append(
            Measurement(metric="temperature", value=float(payload["temperature_c"]), unit="°C")
        )

    if "flow_l_min" in payload:
        measurements.append(
            Measurement(metric="flow_rate", value=float(payload["flow_l_min"]), unit="L/min")
        )

    return _build_event(source_name, schema_family, payload, measurements)


def normalize_airlock_topic(source_name, schema_family, payload):
    # Schema: topic.airlock.v1 fields: cycles_per_hour (number), last_state (string enum)
    measurements = []

    if "cycles_per_hour" in payload:
        measurements.append(
            Measurement(metric="cycles_per_hour", value=float(payload["cycles_per_hour"]), unit="cycles/h")
        )

    # last_state è un enum stringa (IDLE/PRESSURIZING/DEPRESSURIZING), non un numero
    # Lo salviamo come stringa nel campo unit per non perdere l'informazione
    if "last_state" in payload:
        measurements.append(
            Measurement(metric="last_state", value=0.0, unit=str(payload["last_state"]))
        )

    return _build_event(source_name, schema_family, payload, measurements)