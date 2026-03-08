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

-- Insert test rules
INSERT INTO rules (
    name,
    sensor_name,
    metric_name,
    operator,
    threshold_value,
    unit,
    actuator_name,
    target_state,
    rule_enabled
)
VALUES
(
    'High temperature cooling',
    'greenhouse_temperature',
    'temperature_c',
    '>',
    0,
    'C',
    'cooling_fan',
    'ON',
    TRUE
),
(
    'Low humidity humidifier',
    'entrance_humidity',
    'humidity',
    '<',
    35,
    '%',
    'entrance_humidifier',
    'ON',
    TRUE
),
(
    'High CO2 ventilation',
    'co2_hall',
    'co2',
    '>',
    900,
    'ppm',
    'hall_ventilation',
    'ON',
    TRUE
);