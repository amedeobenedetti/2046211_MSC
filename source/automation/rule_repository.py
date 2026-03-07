from ..db import SessionLocal
from .common.models import RuleModel
from .common.rules import AutomationRule

def get_rules():
    db = SessionLocal()
    rows = db.query(RuleModel).all()
    rules = [
        AutomationRule(
            id=r.id,
            sensor_name=r.sensor_name,
            metric_name=r.metric_name,
            operator=r.operator,
            threshold=r.threshold,
            actuator_name=r.actuator_name,
            target_state=r.target_state
        )
        for r in rows
    ]
    db.close()
    return rules

def create_rule(rule: AutomationRule):
    db = SessionLocal()
    model = RuleModel(
        sensor_name=rule.sensor_name,
        metric_name=rule.metric_name,
        operator=rule.operator,
        threshold=rule.threshold,
        actuator_name=rule.actuator_name,
        target_state=rule.target_state
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    db.close()
    return model