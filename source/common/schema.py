from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime, timezone

class Measurements(BaseModel):
    metric: str = Field(..., description="The name of the metric")
    value: float = Field(..., description="The value of the metric")
    unit: str = Field(..., description="The unit of the metric")

class UnifiedEvent(BaseModel):
    type: Literal[
        "rest.scalar.v1",
        "rest.chemistry.v1",
        "rest.particulate.v1",
        "rest.level.v1",
        "topic.power.v1",
        "topic.environment.v1",
        "topic.thermal_loop.v1",
        "topic.airlock.v1",
    ] = Field(..., description="The type of the event")
    source: Literal["rest", "topic"] = Field(..., description="The source of the event, either 'rest' or 'topic'")
    device_id: str = Field(..., description="The unique identifier of the device that generated the event")
    timestamp: datetime = Field(lambda: datetime.now(timezone.utc), description="The timestamp of the event")
    status: Literal["ok", "warning"] = Field(..., description="The status of the event, either 'ok' or 'warning'")
    measurements: List[Measurements] = Field(..., description="The measurements associated with the event")