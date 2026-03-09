CREATE DATABASE mars;


CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sensor_name VARCHAR(255) NOT NULL,
    metric_name VARCHAR(255) NOT NULL,
    operator VARCHAR(10) NOT NULL CHECK (operator IN ('<', '<=', '=', '>', '>=')),
    threshold_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    actuator_name VARCHAR(255) NOT NULL,
    target_state VARCHAR(10) NOT NULL CHECK (target_state IN ('ON', 'OFF')),
    rule_enabled BOOLEAN NOT NULL DEFAULT TRUE
);
