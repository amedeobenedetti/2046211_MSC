CREATE DATABASE IF NOT EXISTS mars_db;

CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    sensor_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    operator TEXT NOT NULL,
    threshold FLOAT NOT NULL,
    actuator_name TEXT NOT NULL,
    target_state TEXT NOT NULL
);