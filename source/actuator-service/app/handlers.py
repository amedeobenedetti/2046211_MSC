import logging
import asyncio
from app.common.models import UnifiedEvent, ActuatorEvent
from app.simulator_client import SimulatorClient
from app.common.rabbitmq_config import SIMULATOR_BASE_URL

logger = logging.getLogger(__name__)

simulator = SimulatorClient(SIMULATOR_BASE_URL)

async def post_actuator_cmd(a_event: ActuatorEvent):
    response = simulator.post_actuator_command(a_event.actuator_name, {"state": a_event.target_state})

    logger.info(f"Sent actuator command for {a_event.sensor_name} with state {a_event.target_state}. Simulator response: {response['actuator']} set to {response['state']}")

def handle_actuator_event(event: UnifiedEvent) -> None:
    logger.info("Received event: event_id=%s", event.event_id)
    if event.event_type != "actuator":
        return 
    
    a_event = ActuatorEvent.model_validate(event.event_payload)
    
    asyncio.run(post_actuator_cmd(a_event))

    # response = simulator.post_actuator_command(a_event.sensor_name, {"state": a_event.target_state})

    # logger.info(f"Sent actuator command for {a_event.sensor_name} with state {a_event.target_state}. Simulator response: {response.actuator_state} set to {response.state}")
