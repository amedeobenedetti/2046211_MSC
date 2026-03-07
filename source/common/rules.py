from pydantic import BaseModel
from typing import Literal, Optional

class AutomationRule(BaseModel):
    id: Optional[int] = None
    sensor_name: str
    metric_name: str
    operator: Literal["<", ">", "<=", ">=", "==", "!="]
    threshold: float
    actuator_name: str
    target_state: Literal["ON", "OFF"]