import requests

SIMULATOR_URL = "http://simulator:8080"


def set_actuator(actuator_name: str, state: str):

    url = f"{SIMULATOR_URL}/api/actuators/{actuator_name}"

    requests.post(
        url,
        json={"state": state},
        timeout=5
    )