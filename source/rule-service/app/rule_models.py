from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, func

from app.db import Base


class Rule(Base):
    """SQLAlchemy model for the Rule entity"""
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sensor_name = Column(String(255), nullable=False, index=True)
    metric_name = Column(String(255), nullable=False)
    operator = Column(String(10), nullable=False)
    threshold_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    actuator_name = Column(String(255), nullable=False)
    target_state = Column(String(10), nullable=False)
    rule_enabled = Column(Boolean, nullable=False, default=True)
