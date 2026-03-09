from sqlalchemy import select, update, insert, delete

from app.common.models import RuleEvent
from app.db import SessionLocal
from app.rule_models import Rule


class RulesRepository:
    def get_rules(self) -> list[Rule]:
        with SessionLocal() as session:
            stmt = select(Rule).order_by(Rule.id)
            return list(session.execute(stmt).scalars().all())
        
    def get_rule_from_id(self, id) -> Rule:
        with SessionLocal() as session:
            stmt = (select(Rule).where(Rule.id == id))
            return session.execute(stmt).scalar_one_or_none()

    def get_rules_for_sensor(self, sensor_name: str) -> list[Rule]:
        with SessionLocal() as session:
            stmt = (
                select(Rule)
                .where(Rule.sensor_name == sensor_name)
            )
            
            return list(session.execute(stmt).scalars().all())
        
    def set_rule_state(self, rule_id: int, enabled: bool) -> None:
        set_to = enabled
        with SessionLocal() as session:
            stmt = (
                select(Rule)
                .where(Rule.id == rule_id)
            )
            rule = session.execute(stmt).scalar_one_or_none()
            if rule is not None:
                stmt = (
                    update(Rule)
                    .where(Rule.id == rule_id)
                    .values(rule_enabled = set_to)
                )
                session.execute(stmt)
                session.commit()

    def update_rule(self, rule: Rule) -> None:
        with SessionLocal() as session:
            stmt = (
                update(Rule)
                .where(Rule.id == rule.id) 
                .values(
                    name=rule.name,
                    sensor_name=rule.sensor_name,
                    metric_name=rule.metric_name,
                    operator=rule.operator,
                    threshold_value=rule.threshold_value,
                    unit=rule.unit,
                    actuator_name=rule.actuator_name,
                    target_state=rule.target_state,
                    rule_enabled=rule.rule_enabled,
                )
            )
            session.execute(stmt)
            session.commit()
    
    def add_rule(self, new_rule: RuleEvent) -> None:
        with SessionLocal() as session:
            stmt = (
                insert(Rule)
                .values(
                    name=new_rule.rule_name,
                    sensor_name=new_rule.sensor_name,
                    metric_name=new_rule.metric_name,
                    operator=new_rule.operator,
                    threshold_value=new_rule.threshold_value,
                    unit=new_rule.unit,
                    actuator_name=new_rule.actuator_name,
                    target_state=new_rule.target_state,
                    rule_enabled=new_rule.rule_enabled,
                )
            ).returning(Rule.id)
            result = session.execute(stmt)
            session.commit()
            return result.scalar_one()

    def delete_rule(self, rule_id: int) -> None:
        with SessionLocal() as session:
            stmt = (
                delete(Rule)
                .where(Rule.id == rule_id)
            )
            session.execute(stmt)
            session.commit()
            

    