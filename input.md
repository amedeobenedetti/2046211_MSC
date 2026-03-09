# SYSTEM OVERVIEW

The Mars Habitat Automation Platform is a distributed system designed to monitor and control a simulated Mars habitat environment.

The system collects data from heterogeneous IoT devices provided by a simulator. These devices expose data through two mechanisms:

* REST sensors that must be periodically polled
* Telemetry streams that publish events asynchronously

Incoming data is normalized into a unified internal event format and distributed through a message broker to the internal services.

The system processes sensor data in real time and evaluates automation rules defined by the user. When a rule condition is satisfied, the system triggers the corresponding actuator through the simulator API.

The platform also provides a real-time dashboard that allows users to:

* monitor sensor values
* observe actuator states
* create and manage automation rules
* manually control actuators

The system is implemented as a distributed event-driven architecture composed of multiple microservices communicating through RabbitMQ and using PostgreSQL for persistent rule storage.

# USER STORIES

1) As a user, I want to see the latest value of all sensors so that I can monitor the habitat environment.

2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

3) As a user, I want to visualize sensor data on a dashboard so that I can easily understand the state of the habitat.

4) As a user, I want to see the status of each sensor (ok or warning) so that I can quickly identify potential issues.

5) As a user, I want to view the measurements associated with each sensor so that I can understand what metrics are being monitored.

6) As a user, I want to see the list of available actuators so that I know which systems can be controlled.

7) As a user, I want to see the current state of each actuator so that I know which systems are currently active.

8) As a user, I want to manually toggle an actuator so that I can directly control habitat systems when needed.

9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11) As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12) As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

13) As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

14) As a user, I want the system to automatically trigger actuators when rule conditions are satisfied so that the habitat environment stays safe.

15) As a user, I want to receive a notification when a rule is triggered so that I know when the system performs an automatic action.

16) As a user, I want the dashboard to update automatically when new sensor data arrives so that the displayed information is always up to date.

17) As a user, I want to identify which sensor generated an event so that I can trace the origin of the data.

18) As a user, I want to see sensor values with their measurement units so that the information is clear and understandable.

19) As a user, I want to monitor environmental parameters such as temperature, humidity and air quality so that I can ensure safe habitat conditions.

20) As a user, I want the system to remain operational after a restart while keeping the automation rules so that automation continues to work.

# EVENT SCHEMA

To handle heterogeneous device payloads, the platform converts all incoming data into a Unified event schema. This schema represents the normalized internal event exchanged between services.

## Event structure

```json
{
  "event_id": "string",
  "source_kind": "rest_sensor | telemetry_topic",
  "source_name": "string",
  "schema_family": "string",
  "timestamp": "datetime",
  "status": "ok | warning",
  "measurements": [
    {
      "metric": "string",
      "value": 0.0,
      "unit": "string"
    }
  ]
}
```

### Field description

* **event_id**: Unique identifier of the event
* **source_kind**: Indicates whether the event originates from a REST sensor or a telemetry topic
* **source_name**: Logical identifier of the sensor or telemetry topic
* **schema_family**: Schema category describing the original device payload
* **timestamp**: Time at which the measurement was generated
* **status**: Status of the measurement provided by the simulator (`ok` or `warning`)
* **measurements**: List of normalized measurements associated with the event

## Measurement Structure

Each event contains metadata about the source device and a list of measurements associated with the event. Each measurement contains:

* **metric**: Name of the measured metric
* **value**: Numeric value of the measured value
* **unit**: Unit associated with the measurement

# RULE MODEL

Automation rules define how the system reacts to sensor measurements. A rule evaluates a condition on a specific sensor metric and triggers an actuator action when the condition is satisfied.

## Rule Structure

```json
{
  "id": 1,
  "sensor_name": "string",
  "metric_name": "string",
  "operator": "< | > | <= | >= | == | !=",
  "threshold": 0.0,
  "actuator_name": "string",
  "target_state": "ON | OFF"
}
```
### Field description

* **id**: Unique identifier of the rule
* **sensor_name**: Name of the sensor that triggers the rule
* **metric_name**: Name of the metric used in the condition
* **operator**: Comparison operator used for the rule
* **threshold**: Threshold value used for the comparison
* **actuator_name**: Target actuator that will be triggered
* **target_state**: Desired actuator state (ON or OFF)

## Rule evaluation

Rules are evaluated whenever a new event is received. The automation engine performs the following steps:

1) Receive a normalized event from the message broker.

2) Extract all measurements contained in the event.

3) Check if any rule is associated with the sensor and metric.

4) Evaluate the rule condition using the specified operator.

5) If the condition is satisfied, emit an actuator command that will be executed by the actuator service through the simulator API.

Rules follow the structure:

IF `<sensor_name>` `<operator>` `<value>` `[unit]`
THEN set `<actuator_name>` to `ON` | `OFF`

Rules are stored persistently in a database so that they survive service restarts.

### Example rule

IF greenhouse_temperature > 28 °C
THEN set cooling_fan to ON

This rule automatically activates the cooling fan when the greenhouse temperature exceeds 28 degrees.