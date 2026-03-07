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

The system is implemented as a distributed event-driven architecture composed of multiple services communicating through a message broker.

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


# CONTAINERS:

## CONTAINER_NAME: mars-simulator

### DESCRIPTION:
This container runs the Mars IoT simulator. It simulates heterogeneous sensors, telemetry streams, and actuators representing the Mars habitat infrastructure.

### USER STORIES:
1) As a user, I want to see the latest value of all sensors so that I can monitor the habitat environment.

2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

4) As a user, I want to see the status of each sensor (ok or warning) so that I can quickly identify potential issues.

5) As a user, I want to view the measurements associated with each sensor so that I can understand what metrics are being monitored.

6) As a user, I want to see the list of available actuators so that I know which systems can be controlled.

7) As a user, I want to see the current state of each actuator so that I know which systems are currently active.

17) As a user, I want to identify which sensor generated an event so that I can trace the origin of the data.

18) As a user, I want to see sensor values with their measurement units so that the information is clear and understandable.

19) As a user, I want to monitor environmental parameters such as temperature, humidity and air quality so that I can ensure safe habitat conditions.

### PORTS:
8080:8080

### DESCRIPTION:
The simulator exposes REST APIs used to retrieve sensor data, discover telemetry topics, and control actuators.

### PERSISTENCE EVALUATION
The simulator does not persist data. It only generates simulated sensor measurements and actuator states during runtime.

### EXTERNAL SERVICES CONNECTIONS
The simulator is accessed by internal services through HTTP requests.


## CONTAINER_NAME: rabbitmq

### DESCRIPTION:
RabbitMQ acts as the message broker used for asynchronous communication between system services.

### USER STORIES:
2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

13) As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

16) As a user, I want the dashboard to update automatically when new sensor data arrives so that the displayed information is always up to date.

### PORTS:
5672:5672
15672:15672

### DESCRIPTION:
RabbitMQ receives normalized sensor events from the ingestion service and distributes them to subscribed services such as the processing service.

### PERSISTENCE EVALUATION
In the current configuration, messages are transient and not persisted.

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ communicates with the ingestion service (publisher) and the processing service (consumer).


## CONTAINER_NAME: mars-ingestion-service

### DESCRIPTION:
The ingestion service is responsible for collecting sensor data from the Mars simulator and converting heterogeneous payloads into a unified event schema.

### USER STORIES:
1) As a user, I want to see the latest value of all sensors so that I can monitor the habitat environment.

2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

4) As a user, I want to see the status of each sensor (ok or warning) so that I can quickly identify potential issues.

5) As a user, I want to view the measurements associated with each sensor so that I can understand what metrics are being monitored.

17) As a user, I want to identify which sensor generated an event so that I can trace the origin of the data.

18) As a user, I want to see sensor values with their measurement units so that the information is clear and understandable.

19) As a user, I want to monitor environmental parameters such as temperature, humidity and air quality so that I can ensure safe habitat conditions.

### PORTS:
8000:8000

### PERSISTENCE EVALUATION
This service does not store data. It only transforms incoming sensor payloads and publishes normalized events.

### EXTERNAL SERVICES CONNECTIONS
- Mars Simulator REST API
- RabbitMQ message broker

### MICROSERVICES:

#### MICROSERVICE: ingestion-service
- TYPE: backend
- DESCRIPTION: Polls REST sensors from the simulator, normalizes payloads, and publishes sensor events to RabbitMQ.
- PORTS: 8000
- TECHNOLOGICAL SPECIFICATION:
The service is implemented in Python and uses Pydantic models to represent normalized events and measurements.
- SERVICE ARCHITECTURE:
The service periodically polls sensors from the simulator, converts the payloads into UnifiedEvent objects, and publishes them to the RabbitMQ exchange.


## CONTAINER_NAME: mars-processing-service

### DESCRIPTION:
The processing service consumes normalized sensor events and evaluates automation rules.

### USER STORIES:
8) As a user, I want to manually toggle an actuator so that I can directly control habitat systems when needed.

9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11) As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12) As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

13) As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

14) As a user, I want the system to automatically trigger actuators when rule conditions are satisfied so that the habitat environment stays safe.

15) As a user, I want to receive a notification when a rule is triggered so that I know when the system performs an automatic action.

### PORTS:
8001:8001

### PERSISTENCE EVALUATION
The service reads and manages automation rules stored in the PostgreSQL database.

### EXTERNAL SERVICES CONNECTIONS
- RabbitMQ
- Mars Simulator (actuator API)
- PostgreSQL database

### MICROSERVICES:

#### MICROSERVICE: processing-service
- TYPE: backend
- DESCRIPTION: Consumes sensor events from RabbitMQ and evaluates automation rules.
- PORTS: 8001
- TECHNOLOGICAL SPECIFICATION:
Implemented in Python using an event-driven architecture and rule evaluation logic.
- SERVICE ARCHITECTURE:
When a new event arrives, the service extracts measurements and checks whether any automation rule conditions are satisfied. If a condition is met, the service triggers the corresponding actuator through the simulator API.


## CONTAINER_NAME: mars-db

### DESCRIPTION:
This container runs a PostgreSQL database used to persist automation rules.

### USER STORIES:
9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11) As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12) As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

20) As a user, I want the system to remain operational after a restart while keeping the automation rules so that automation continues to work.

### PORTS:
5432:5432

### PERSISTENCE EVALUATION
Automation rules are stored persistently so that they remain available even after system restarts.

### EXTERNAL SERVICES CONNECTIONS
The database is accessed by the processing service.

### MICROSERVICES:

#### MICROSERVICE: postgres-db
- TYPE: backend
- DESCRIPTION: Stores automation rules used by the processing service.
- PORTS: 5432
- TECHNOLOGICAL SPECIFICATION:
PostgreSQL database initialized with an SQL script included in the project.
- SERVICE ARCHITECTURE:
The database stores rule records containing sensor conditions and actuator actions.

- DB STRUCTURE:

**rules** : | **id** | sensor_name | metric_name | operator | threshold | actuator_name | target_state |