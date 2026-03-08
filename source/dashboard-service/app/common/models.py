from datetime import datetime, timezone
from typing import List, Literal, Any
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Measurement(BaseModel):
    metric: str = Field(..., description="The name of the metric")
    value: float = Field(..., description="The value of the metric")
    unit: str = Field(..., description="The unit of the metric")

class UnifiedEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: Literal["measurement", "actuator"]
    event_payload: Any


class MeasurementEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    source_kind: Literal["rest_sensor", "telemetry_topic"] = Field(
        ...,
        description="The source kind of the event"
    )
    source_name: str = Field(
        ...,
        description="The logical name of the sensor or telemetry topic"
    )
    schema_family: Literal[
        "rest.scalar.v1",
        "rest.chemistry.v1",
        "rest.particulate.v1",
        "rest.level.v1",
        "topic.power.v1",
        "topic.environment.v1",
        "topic.thermal_loop.v1",
        "topic.airlock.v1",
    ] = Field(
        ...,
        description="The schema family of the original payload"
    )
    timestamp: datetime = Field(
        default_factory=utc_now,
        description="The timestamp of the event"
    )
    status: Literal["ok", "warning"] = Field(
        ...,
        description="The status of the event"
    )
    measurements: List[Measurement] = Field(
        ...,
        description="The normalized measurements associated with the event"
    )

class ActuatorEvent(BaseModel):
    event_id: str
    rule_id: int
    rule_name: str
    sensor_name: str
    metric_name: str
    actuator_name: str
    target_state: str
    measured_value: float
    threshold_value: float
    operator: str
    unit: str | None = None