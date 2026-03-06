from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class Measurements(BaseModel):
    metric: str = Field(..., description="The name of the metric")
    value: float = Field(..., description="The value of the metric")
    unit: str = Field(..., description="The unit of the metric")

class UnifiedEvent(BaseModel):
    type: str = Field(..., description="The type of the event")
    source: Literal["rest", "topic"] = Field(..., description="The source of the event, either 'rest' or 'topic'")
    schema_family: str = Field(..., description="The schema family of the event")
    required: List[str] = Field(..., description="List of required fields for the event")
    timestamp: datetime = Field(..., description="The timestamp of the event")
    status: Literal["ok", "failure"] = Field(..., description="The status of the event, either 'ok' or 'failure'")
    measurements: Measurements = Field(..., description="The measurements associated with the event")