from sqlalchemy import select

from app.db import SessionLocal
from app.rule_models import Rule


class RulesRepository:
    def get_enabled_rules(self) -> list[Rule]:
        with SessionLocal() as session:
            stmt = select(Rule).where(Rule.rule_enabled.is_(True))
            return list(session.execute(stmt).scalars().all())

    def get_enabled_rules_for_sensor(self, sensor_name: str) -> list[Rule]:
        with SessionLocal() as session:
            stmt = (
                select(Rule)
                .where(Rule.rule_enabled.is_(True))
                .where(Rule.sensor_name == sensor_name)
            )
            
            return list(session.execute(stmt).scalars().all())