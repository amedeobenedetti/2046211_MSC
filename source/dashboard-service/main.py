import logging
from contextlib import asynccontextmanager
from app.common.rabbitmq_config import (
    RABBITMQ_EXCHANGE,
    RABBITMQ_REST_SENSORS_ROUTING_KEY,
    SIMULATOR_BASE_URL,
    RULES_ENGINE_URL
)
from app.handlers import (
    handle_measurement_event, 
    get_state, 
    get_state_by_source, 
    send_actuator_command, 
    set_rule_state,
    update_rule,
    add_rule,
    delete_rule
)
from fastapi import FastAPI, HTTPException, Body
from fastapi.concurrency import run_in_threadpool

from app.common.rabbitmq_config import RabbitMQConsumer
from fastapi.middleware.cors import CORSMiddleware
from app.simulator_client import HTTPxClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


consumer = None

def run_consumer() -> None:
    global consumer
    consumer = RabbitMQConsumer("dashboard",RABBITMQ_EXCHANGE, [f"{RABBITMQ_REST_SENSORS_ROUTING_KEY}.#"], handle_measurement_event)
    consumer.connect()
    run_in_threadpool(consumer.start_consuming())
    print("Consumer started")


import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
    print("Startup Completed!")
    yield
    print("Shutdown Completed!")


app = FastAPI(title="Dashboard Service", version="0.1.0", lifespan=lifespan)

origins = [
    "http://localhost:8002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_client = HTTPxClient(SIMULATOR_BASE_URL)

@app.get("/health")
async def health() -> dict:
    """"Health check endpoint"""
    return {"status": "ok"}


# Sensor Endpoints
@app.get("/state")
async def get_state_s() -> dict:
    """Returns the current sensors-state of the system"""
    return await run_in_threadpool(get_state)

@app.get("/sensors/{source_name}")
async def get_state_from_name(source_name: str) -> dict:
    """Returns the current state of a specific sensor by its name"""
    def get_source(source_name:str):
        state = get_state_by_source(source_name)

        if state is None:
            raise HTTPException(status_code=404, detail="Source not found")
        return state
    return await run_in_threadpool(get_source, source_name)

@app.get("/sensors")
def get_sensors_list():
    """Returns the list of sensors"""
    return web_client.get_sensors_list()
    

# Telemetry Endpoints
# TODO: Implement telemetry endpoints


# Actuator Endpoints
@app.get("/actuators")
def get_actuators_list():
    """Returns the list of actuators"""
    return web_client.get_actuators_list()

@app.post("/actuators/{actuator_name}")
async def send_command(actuator_name: str, command: str = Body(..., embed=True)):
    """Send a command to an actuator (is overwritten by eventual rule events)"""
    return await run_in_threadpool(send_actuator_command, actuator_name, command)


# Rule Endpoints
@app.get("/rules")
def get_rules_list():
    """
    Returns the list of rules
    """
    return web_client.request_url(f"{RULES_ENGINE_URL}/rules", "GET")
    pass

@app.post("/rules/{rule_id}")
async def set_rule(rule_id: int, state: bool = Body(..., embed=True)):
    """Enable or disable a rule by its ID"""
    return await run_in_threadpool(set_rule_state, rule_id, state)

@app.delete("/rules/{rule_id}")
def delete_delete_rule(rule_id: int):
    """
    Delete a rule
    """
    pass

@app.put("/rule")
def create_rule(rule: dict):
    """
    Create a new rule
    """
    pass

@app.put("/rules/{rule_id}")
async def put_update_rule(rule_id: int, rule: dict = Body(..., embed=True)):
    """
    Update a rule
    """
    return await run_in_threadpool(update_rule, rule)

    



    