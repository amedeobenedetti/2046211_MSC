# SYSTEM DESCRIPTION

The Mars Habitat Automation Platform is a distributed system designed to monitor and control a simulated Mars habitat environment.

The system collects data from heterogeneous devices provided by a simulator. These devices expose data through two mechanisms:

* REST sensors that must be periodically polled
* Telemetry streams that publish events asynchronously

Incoming data is normalized into a unified internal event format and distributed through a message broker to the internal services.

The system processes sensor data in real time and evaluates automation rules defined by the user. When a rule condition is satisfied, the system triggers the corresponding actuator through the simulator API.

The platform also provides a real-time dashboard that allows users to:

* monitor sensor values
* observe actuator states
* create and manage automation rules

The system is implemented as a distributed event-driven architecture composed of multiple services communicating through a message broker.

# EVENT SCHEMA

All incoming sensor data is normalized into a unified internal event format called **UnifiedEvent**.

This schema allows different services of the system to process events in a consistent way regardless of the original device protocol.

Each event contains metadata about the source device and a list of measurements associated with the event.

## UnifiedEvent structure

Fields:

* **type**: schema family of the event (e.g. `rest.scalar.v1`, `topic.power.v1`)
* **source**: origin of the event (`rest` or `topic`)
* **device_id**: identifier of the device that generated the event
* **timestamp**: timestamp of the event
* **status**: event status (`ok` or `warning`)
* **measurements**: list of measurements associated with the event

Each measurement contains:

* **metric**: name of the metric
* **value**: measured value
* **unit**: measurement unit

## Example Event

```
{
  "type": "rest.scalar.v1",
  "source": "rest",
  "device_id": "greenhouse_temperature",
  "timestamp": "2026-03-05T10:15:30Z",
  "status": "ok",
  "measurements": [
    {
      "metric": "temperature",
      "value": 27.3,
      "unit": "C"
    }
  ]
}
```

# RULE MODEL

The automation engine supports simple event-triggered rules.

Rules follow the structure:

IF `<sensor_name>` `<operator>` `<value>` `[unit]`
THEN set `<actuator_name>` to `ON` | `OFF`

Example rule:

IF greenhouse_temperature > 28 °C
THEN set cooling_fan to ON

Supported operators:

* <
* <=
* =
* >
* > =

Rules are stored persistently in a database so that they survive service restarts.

# USER STORIES

1. As a user, I want to see the latest value of all sensors so that I can monitor the habitat environment.

2. As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

3. As a user, I want to visualize sensor data on a dashboard so that I can easily understand the state of the habitat.

4. As a user, I want to see the status of each sensor (ok or warning) so that I can quickly identify potential issues.

5. As a user, I want to view the measurements associated with each sensor so that I can understand what metrics are being monitored.

6. As a user, I want to see the list of available actuators so that I know which systems can be controlled.

7. As a user, I want to see the current state of each actuator so that I know which systems are currently active.

8. As a user, I want to manually toggle an actuator so that I can directly control habitat systems when needed.

9. As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10. As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11. As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12. As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

13. As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

14. As a user, I want the system to automatically trigger actuators when rule conditions are satisfied so that the habitat environment stays safe.

15. As a user, I want to receive a notification when a rule is triggered so that I know when the system performs an automatic action.

16. As a user, I want the dashboard to update automatically when new sensor data arrives so that the displayed information is always up to date.

17. As a user, I want to identify which sensor generated an event so that I can trace the origin of the data.

18. As a user, I want to see sensor values with their measurement units so that the information is clear and understandable.

19. As a user, I want to monitor environmental parameters such as temperature, humidity and air quality so that I can ensure safe habitat conditions.

20. As a user, I want the system to remain operational after a restart while keeping the automation rules so that automation continues to work.