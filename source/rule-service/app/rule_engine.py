from app.common.models import MeasurementEvent, ActuatorEvent
from app.rule_models import Rule
from uuid import uuid4
from pydantic import BaseModel


class RuleEngine:
    def evaluate_event(self, event: MeasurementEvent, rules: list[Rule]) -> list[ActuatorEvent]:
        triggered: list[ActuatorEvent] = []

        for rule in rules:
            if not rule.rule_enabled:
                continue
            
            matching_measurement = next(
                (m for m in event.measurements if m.metric == rule.metric_name),
                None,
            )

            if matching_measurement is None:
                continue

            if rule.unit and matching_measurement.unit and rule.unit != matching_measurement.unit:
                continue

            if self._compare(
                matching_measurement.value,
                rule.operator,
                rule.threshold_value,
            ):
                triggered.append(
                    ActuatorEvent(
                        event_id=str(uuid4()),
                        rule_id=rule.id,
                        rule_name=rule.name,
                        sensor_name=rule.sensor_name,
                        metric_name=rule.metric_name,
                        actuator_name=rule.actuator_name,
                        target_state=rule.target_state,
                        measured_value=matching_measurement.value,
                        threshold_value=rule.threshold_value,
                        operator=rule.operator,
                        unit=rule.unit,
                    )
                )

        return triggered

    def _compare(self, value: float, operator: str, threshold: float) -> bool:
        if operator == "<":
            return value < threshold
        if operator == "<=":
            return value <= threshold
        if operator == "=":
            return value == threshold
        if operator == ">":
            return value > threshold
        if operator == ">=":
            return value >= threshold

        raise ValueError(f"Unsupported operator: {operator}")