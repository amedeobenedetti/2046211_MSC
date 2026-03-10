# SYSTEM OVERVIEW

The Mars Habitat Control Panel is a distributed system designed to monitor and control a simulated Mars habitat environment.

The system collects data from heterogeneous IoT devices provided by a simulator. These devices expose data through two mechanisms:

* REST sensors that must be periodically polled
* Telemetry streams that publish events asynchronously

Incoming data is normalized into a unified internal event format and distributed through a message broker to the internal services.

The system processes sensor data in real time and evaluates automation rules defined by the user. When a rule condition is satisfied, the system triggers the corresponding actuator through the simulator API.

The platform also provides a real-time dashboard that allows users to:

* monitor sensor values
* create and manage automation rules
* observe actuator states
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


# CONTAINERS:

## CONTAINER_NAME: mars-simulator

### DESCRIPTION:
Runs the Mars IoT simulator. It simulates heterogeneous sensors, telemetry streams, and actuators representing the Mars habitat infrastructure.

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
The simulator container is an external dependency packaged as a prebuilt image. It exposes habitat discovery endpoints, REST sensor data, telemetry topic streams, and actuator control APIs used by the other services.

### PERSISTENCE EVALUATION
The simulator does not persist data.

### EXTERNAL SERVICES CONNECTIONS
The simulator is accessed by internal services through HTTP requests.

#### MICROSERVICE: mars-simulator
- TYPE: external system
- DESCRIPTION: Simulates the Mars habitat environment and exposes APIs for sensors, telemetry, and actuators.
- PORTS: 8080


## CONTAINER_NAME: rabbitmq

### DESCRIPTION:
Provides the asynchronous event bus used to decouple ingestion, rule evaluation, dashboard updates, and actuator execution.

### USER STORIES:
2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

13) As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

16) As a user, I want the dashboard to update automatically when new sensor data arrives so that the displayed information is always up to date.

### PORTS:
5672:5672
15672:15672

### DESCRIPTION:
The RabbitMQ container is the message broker of the system. It hosts the topic exchange used to route measurement, rule, and actuator events among microservices, and exposes the management interface for inspection.

### PERSISTENCE EVALUATION
The RabbitMQ container is configured without an active persistent volume, so broker state is not guaranteed to survive container recreation.

### EXTERNAL SERVICES CONNECTIONS
RabbitMQ does not integrate with third-party or external platform services. It is connected only to the internal microservices of this system.

#### MICROSERVICE: rabbitmq
- TYPE: middleware
- DESCRIPTION: Routes events between microservices using topic-based messaging.
- PORTS: 5672, 15672


## CONTAINER_NAME: mars-ingestion-service

### DESCRIPTION:
Manages sensor acquisition from the Mars simulator, including periodic polling of REST sensors, subscription to telemetry streams, normalization of heterogeneous payloads, and publication of measurement events to RabbitMQ.

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

### DESCRIPTION:
The Ingestion-Service container is responsible for interacting with the external Mars simulator. It discovers REST sensors, polls them every few seconds, subscribes to telemetry topics through streaming endpoints, converts raw payloads into a common event schema, and publishes measurement events on RabbitMQ using dedicated routing keys for REST sensors and telemetry sources.

### PERSISTENCE EVALUATION
This service does not store data. It only transforms incoming sensor payloads and publishes normalized events.

### EXTERNAL SERVICES CONNECTIONS
The Ingestion-Service container connects to the Mars simulator over HTTP and Server-Sent Events, and publishes messages to RabbitMQ.

### MICROSERVICES:

#### MICROSERVICE: ingestion-service
- TYPE: backend
- DESCRIPTION: Collects sensor and telemetry data from the simulator, normalizes it, and publishes unified measurement events.
- PORTS: 8000
- TECHNOLOGICAL SPECIFICATION:
The microservice is developed in Python and uses FastAPI.
It uses the following libraries and technologies:
    - FastAPI: Provides the HTTP application and lifecycle hooks.
    - Uvicorn: Runs the ASGI application inside the container.
    - HTTPX: Performs HTTP requests to the simulator and consumes telemetry streams.
    - Pika: Publishes normalized events to RabbitMQ.
    - Pydantic: Defines the shared event schemas used across services.
- SERVICE ARCHITECTURE:
The service is realized with:
    - a FastAPI entrypoint that starts background tasks on startup
    - a poller module that discovers and periodically polls REST sensors
    - a telemetry listener that subscribes to simulator telemetry topics
    - a normalizer module that maps multiple schema families into a unified event model
    - a simulator client for the external simulator API
    - shared common models and RabbitMQ utilities

- ENDPOINTS:

    | HTTP METHOD | URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | /health | Returns the service health status | |


## CONTAINER_NAME: mars-rule-service

### DESCRIPTION:
Manages automation rules, including persistence, retrieval, evaluation against measurement events, and generation of actuator trigger events.

### USER STORIES:
9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11) As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12) As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

13) As a user, I want the system to evaluate rules whenever new sensor events arrive so that automation can happen in real time.

14) As a user, I want the system to automatically trigger actuators when rule conditions are satisfied so that the habitat environment stays safe.

15) As a user, I want to receive a notification when a rule is triggered so that I know when the system performs an automatic action.

### PORTS:
8001:8001

### DESCRIPTION:
The Rule-Service container stores automation rules in PostgreSQL and consumes both measurement events and rule-management events from RabbitMQ. When a measurement matches an enabled rule, the service creates an actuator event and publishes it on the broker. It also exposes an HTTP endpoint used by the dashboard to retrieve the current list of persisted rules.

### PERSISTENCE EVALUATION
The Rule-Service container requires persistent storage because automation rules are stored in PostgreSQL and must remain available after service restarts.

### EXTERNAL SERVICES CONNECTIONS
The Rule-Service container connects to RabbitMQ to consume measurement and rule events and to publish actuator events. It connects to PostgreSQL to store and update rules.

### MICROSERVICES:

#### MICROSERVICE: rule-service
- TYPE: backend
- DESCRIPTION: Persists automation rules, evaluates incoming measurement events, and emits actuator trigger events.
- PORTS: 8001
- TECHNOLOGICAL SPECIFICATION:
The microservice is developed in Python and uses FastAPI.
It uses the following libraries and technologies:
    - FastAPI: Exposes REST endpoints and startup lifecycle management.
    - SQLAlchemy: Maps the Rule entity and executes CRUD operations on PostgreSQL.
    - Psycopg: Supports PostgreSQL connectivity.
    - Pika: Consumes measurement and rule events from RabbitMQ and publishes actuator events.
    - Pydantic: Validates rule and event payloads.
- SERVICE ARCHITECTURE:
The service is realized with:
    - a FastAPI application with a lifespan hook that starts RabbitMQ consumers
    - a repository layer for rule persistence operations
    - a rule engine that compares measurements with thresholds and operators
    - event handlers for measurement events and rule-management events
    - SQLAlchemy models and database session configuration

- ENDPOINTS:

    | HTTP METHOD | URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | /health | Returns the service health status ||
    | GET | /rules | Returns all persisted automation rules | |


## CONTAINER_NAME: mars-dashboard-service

### DESCRIPTION:
Provides the main application API for monitoring the habitat state, inspecting simulator resources, managing automation rules, and issuing manual actuator commands.

### USER STORIES:
1) As a user, I want to see the latest value of all sensors so that I can monitor the habitat environment.

2) As a user, I want to receive real-time updates from sensors so that I can react quickly to environmental changes.

3) As a user, I want to visualize sensor data on a dashboard so that I can easily understand the state of the habitat.

16) As a user, I want the dashboard to update automatically when new sensor data arrives so that the displayed information is always up to date.

17) As a user, I want to identify which sensor generated an event so that I can trace the origin of the data.

18) As a user, I want to see sensor values with their measurement units so that the information is clear and understandable.

### PORTS:
8003:8003

### DESCRIPTION:
The Dashboard-Service container consumes measurement events to maintain the latest in-memory state for each source and exposes HTTP endpoints used by the frontend. It also proxies simulator resource discovery requests, forwards rule-management commands through RabbitMQ, and publishes manual actuator commands for downstream execution.

### PERSISTENCE EVALUATION
The Dashboard-Service container does not require persistent storage. It keeps the latest known state of each source in memory.

### EXTERNAL SERVICES CONNECTIONS
The Dashboard-Service container connects to RabbitMQ to consume measurement events and publish rule or actuator events. It also connects to the Mars simulator to retrieve the lists of sensors, telemetry topics, and actuators, and connects to the Rule-Service HTTP API to retrieve rules.

### MICROSERVICES:

#### MICROSERVICE: dashboard-service
- TYPE: backend
- DESCRIPTION: Exposes monitoring, actuator-control, and rule-management endpoints for the frontend and maintains an in-memory state store.
- PORTS: 8003
- TECHNOLOGICAL SPECIFICATION:
The microservice is developed in Python and uses FastAPI.
It uses the following libraries and technologies:
    - FastAPI: Provides REST endpoints and startup lifecycle logic.
    - Pika: Consumes measurement events and publishes actuator or rule events.
    - HTTPX: Calls the Mars simulator and the Rule-Service HTTP API.
    - Pydantic: Validates event payloads.
    - Threading primitives: Protect the in-memory state store during concurrent access.
- SERVICE ARCHITECTURE:
The service is realized with:
    - a FastAPI application with CORS enabled for the frontend
    - a RabbitMQ consumer that updates the state store from measurement events
    - handler functions for manual actuator commands and rule-management requests
    - a state store component that keeps the latest event for each source
    - an HTTP client for simulator and rule-service integration

- ENDPOINTS:

    | HTTP METHOD | URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | /health | Returns the service health status ||
    | GET | /state | Returns the current state of all known sources | |
    | GET | /sensors/{source_name} | Returns the current state of one source | |
    | GET | /sensors | Returns the list of simulator REST sensors | |
    | GET | /telemetries/{source_name} | Returns the current state of one telemetry source | |
    | GET | /telemetries | Returns the list of telemetry topics |  |
    | GET | /actuators | Returns the list of actuators |  |
    | POST | /actuators/{actuator_name} | Publishes a manual actuator command |  |
    | GET | /rules | Returns the list of automation rules |  |
    | PUT | /rule | Publishes an add-rule event |  |
    | POST | /rules/{rule_id} | Publishes a toggle-rule event |  |
    | PUT | /rules/{rule_id} | Publishes an update-rule event |  |
    | DELETE | /rules/{rule_id} | Publishes a delete-rule event |  |

## CONTAINER_NAME: mars-actuator-service

### DESCRIPTION:
Consumes actuator events and executes the corresponding commands on the Mars simulator actuators.

### USER STORIES:
6) As a user, I want to see the list of available actuators so that I know which systems can be controlled.

7) As a user, I want to see the current state of each actuator so that I know which systems are currently active.

8) As a user, I want to manually toggle an actuator so that I can directly control habitat systems when needed.

14) As a user, I want the system to automatically trigger actuators when rule conditions are satisfied so that the habitat environment stays safe.

### PORTS:
8004:8004

### DESCRIPTION:
The Actuator-Service container listens for actuator trigger events on RabbitMQ. For both manual commands and automatically triggered rule actions, it invokes the Mars simulator actuator API and applies the requested ON or OFF state to the target device.

### PERSISTENCE EVALUATION
The Actuator-Service container does not require persistent storage.

### EXTERNAL SERVICES CONNECTIONS
The Actuator-Service container connects to RabbitMQ to consume actuator events and to the Mars simulator through HTTP to apply actuator commands.

### MICROSERVICES:

#### MICROSERVICE: actuator-service
- TYPE: backend
- DESCRIPTION: Receives actuator events from RabbitMQ and sends the corresponding command to the simulator actuator API.
- PORTS: 8004
- TECHNOLOGICAL SPECIFICATION:
The microservice is developed in Python and uses FastAPI.
It uses the following libraries and technologies:
    - FastAPI: Provides the application container and health endpoint.
    - Pika: Consumes actuator events from RabbitMQ.
    - HTTPX: Sends actuator commands to the Mars simulator.
    - Pydantic: Validates actuator event payloads.
- SERVICE ARCHITECTURE:
The service is realized with:
    - a FastAPI application with a lifespan hook that starts the RabbitMQ consumer
    - an event handler that validates actuator events
    - a simulator client that posts state changes to simulator actuators

- ENDPOINTS:

    | HTTP METHOD | URL | Description | User Stories |
    | ----------- | --- | ----------- | ------------ |
    | GET | /health | Returns the service health status |  |

## CONTAINER_NAME: mars-db

### DESCRIPTION:
Provides persistent relational storage for the automation rules managed by the rule engine.

### USER STORIES:
9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

11) As a user, I want to delete an automation rule so that I can remove behaviours that are no longer needed.

12) As a user, I want to edit an existing automation rule so that I can adjust the system behaviour when conditions change.

20) As a user, I want the system to remain operational after a restart while keeping the automation rules so that automation continues to work.

### PORTS:
5432:5432

### DESCRIPTION:
The postgres container is the relational database used by the platform to store automation rules. It is initialized through the SQL scripts contained in the project and mounted on a local volume so that rule data can survive container restarts and be reused by the Rule-Service.

### PERSISTENCE EVALUATION
The postgres container is the persistence layer of the platform and therefore requires persistent storage. It uses a mounted volume under `./postgres/postgres_data`.

### EXTERNAL SERVICES CONNECTIONS
It is used internally by the Rule-Service for rule persistence.

### MICROSERVICES:

#### MICROSERVICE: postgres-db
- TYPE: database
- DESCRIPTION: Stores the `rules` table used by the rule engine and serves database queries from the Rule-Service.
- PORTS: 5432
- TECHNOLOGICAL SPECIFICATION:
The microservice uses PostgreSQL 16 as relational DBMS.
It is configured with:
    - database user `mars`
    - database password `mars`
    - initial database `mars_rules`
    - initialization SQL scripts mounted from `postgres/init`
- SERVICE ARCHITECTURE:
The service is realized with:
    - a PostgreSQL container image
    - an initialization script that creates the application schema
    - a mounted data directory for persistence across restarts

- DB STRUCTURE:

    **_Rule_** : | **_id_** | name | sensor_name | metric_name | operator | threshold_value | unit | actuator_name | target_state | rule_enabled |

## CONTAINER_NAME: mars-frontend-service

### DESCRIPTION:
Provides the web user interface for habitat monitoring, telemetry visualization, actuator control, and automation rule management.

### USER STORIES:
3) As a user, I want to visualize sensor data on a dashboard so that I can easily understand the state of the habitat.

8) As a user, I want to manually toggle an actuator so that I can directly control habitat systems when needed.

9) As a user, I want to create automation rules so that the system can react automatically to sensor conditions.

10) As a user, I want to view all existing automation rules so that I can understand the current automation logic.

### PORTS:
8002:8002

### DESCRIPTION:
The Frontend-Service container serves the operator-facing web application. It provides a dashboard page with live sensor cards, actuator toggles, telemetry charts, and warning notifications, and a rules page where operators can create, edit, enable, disable, and delete automation rules.

### PERSISTENCE EVALUATION
The frontend does not store data locally.

### EXTERNAL SERVICES CONNECTIONS
The Frontend-Service container communicates with the Dashboard-Service HTTP API. It also loads Chart.js from a CDN to render telemetry graphs in the browser.

### MICROSERVICES:

#### MICROSERVICE: frontend-service
- TYPE: frontend
- DESCRIPTION: Serves the HTML, CSS, and JavaScript pages used by the operator to monitor and control the habitat.
- PORTS: 8002
- PAGES:

    | Name | Description | Related Microservice | User Stories |
    | ---- | ----------- | -------------------- | ------------ |
    | index.html | Displays the monitoring dashboard with sensors, actuators, telemetry charts, and warning notifications | dashboard-service | |
    | rules.html | Displays the automation rule management interface | dashboard-service, rule-service |  |